import torch
import argparse
import os
from datetime import datetime

from VLMs import vlm_roles
from LLMs import llm_roles
from utils import *

torch.manual_seed(1037)

def parse_args():
    """Parse command line arguments for inference."""
    parser = argparse.ArgumentParser(description='Command for video inference')

    # Model paths and device settings
    parser.add_argument('--vlm_model_path', type=str,
                        default='xxxx')
    parser.add_argument('--vlm_device', type=int, default=0)

    # Video and memory extraction settings
    parser.add_argument('--video_url', type=str, default="")
    parser.add_argument('--coarse_memory_extract_prompt', type=str,
                        default="Please observe and understand the given video carefully. "
                                "Describe all the details of this video as comprehensively as possible "
                                "in a smooth and coherent passage. Do not omit any details or prominent "
                                "information. In addition, if there are any texts, subtitles, text overlays, "
                                "or voice-overs in the video, you must explicitly and in detail describe them.")
    parser.add_argument('--coarse_memory_max_pixels', type=int, default=128 * 28 * 28)
    parser.add_argument('--fine_memory_extract_prompt', type=str,
                        default="Please observe all the details in this video very carefully and provide "
                                "a detailed and objective description of what is shown in the video. "
                                "You should pay special attention to any visible texts, subtitles, "
                                "text overlays, or voice-overs in the video to help you better understand "
                                "the content of the video.")
    parser.add_argument('--fine_memory_max_pixels', type=int, default=512 * 28 * 28)

    # Sampling and frame settings
    parser.add_argument('--sampling_fps', type=float, default=1.0)
    parser.add_argument('--short_video_frames', type=int, default=60)
    parser.add_argument('--coarse_overlapping_frames', type=int, default=0)
    parser.add_argument('--fine_sampling_fps', type=float, default=2.0)
    parser.add_argument('--minimal_duration', type=int, default=10)
    parser.add_argument('--fine_overlapping_frames', type=int, default=0)

    # Model and API settings
    parser.add_argument('--vllm', type=bool, default=False)
    parser.add_argument('--api_call', type=bool, default=True)
    parser.add_argument('--api_key', type=str, default="xxxx", help="you should input your api key")
    parser.add_argument('--api_model', type=str, default="deepseek-v3-1-terminus")
    parser.add_argument('--thinking', type=str, default="disabled", help="choose from [disabled, enabled]")

    # Directory settings
    parser.add_argument('--cache_dir', type=str, default='demo_cache')
    parser.add_argument('--fine_memory_dir', type=str, default='fine_memory')
    parser.add_argument('--temp_video_dir', type=str, default='temp_videos')
    parser.add_argument('--infer_batch_size', type=int, default=10)

    return parser.parse_args()


def demo_infer(vlm_model, vlm_processor, args, question, client):
    """
    Main inference function for video question answering.

    Args:
        vlm_model: Vision-language model
        vlm_processor: Vision-language model processor
        args: Command line arguments
        question (str): Question to answer
        client: API client (if using API)

    Returns:
        str: Answer to the question
    """
    print(f"Current Time: {datetime.now()}")
    print(f"Video: {args.video_url}")

    # Phase 1: Coarse memory extraction and summarization
    coarse_memory = vlm_roles.video_coarse_memory_extraction(vlm_model, vlm_processor, args)
    coarse_summary = llm_roles.coarse_memory_summarization(coarse_memory, args, client=client)

    print("Video Summary:")
    print(coarse_summary)
    print("-" * 20)
    print(f"Question: {question}")

    # Phase 2: Answer with coarse memory
    coarse_answer = llm_roles.video_question_answer_with_coarse_memory(coarse_memory, question=question, options=[],args=args, client=client)

    coarse_answer_dict = parse_answer(coarse_answer)
    if coarse_answer_dict is None:
        return None

    if coarse_answer_dict['Confidence']:
        print("="*30)
        print(f"Question: {question}")
        print(f"Answer: {coarse_answer_dict['Answer']}")
        return coarse_answer_dict['Answer']

    # Determine if time-based filtering is needed
    time_flag = not contains_ordinal_number(question)
    video_duration = coarse_memory[-1]['time_period'][1] - coarse_memory[0]['time_period'][0]

    print(f"Time-based filtering: {time_flag}")

    if time_flag:
        # Get relevant time periods for filtering
        question_type_answer = llm_roles.video_question_type_judge_with_coarse_memory(coarse_memory, question, options=[],args=args, client=client)

        question_type_dict = parse_answer(question_type_answer)
        if question_type_dict is None:
            return None

        if question_type_dict['Flag']:
            related_periods = question_type_dict['Time Period']
            filtered_coarse_memory = filter_coarse_memory_by_time_periods(
                coarse_memory, related_periods,
                overlap=args.coarse_overlapping_frames / args.sampling_fps
            )
            max_iterations = 5
        else:
            max_iterations = 5
            filtered_coarse_memory = coarse_memory
    else:
        max_iterations = 5
        filtered_coarse_memory = coarse_memory

    # Initialize memory storage
    fine_memory_history = {
        'time_periods': [],
        'entire_memories': [],
        'divided_memories': []
    }

    super_fine_memory_history = {
        'time_periods': [],
        'entire_memories': [],
        'divided_memories': []
    }

    # Phase 3: Fine-grained memory search
    for iteration in range(max_iterations):
        print(f"Remaining iterations: {max_iterations - iteration}")

        # Find next relevant time period
        time_search_answer = llm_roles.video_question_get_single_related_time_with_coarse_memory(
            filtered_coarse_memory,
            fine_memory_history['entire_memories'], fine_memory_history['divided_memories'],
            question, options=[],
            excluded_time_periods=(fine_memory_history['time_periods'] +
                                   super_fine_memory_history['time_periods']),
            args=args, client=client, duration=video_duration
        )

        time_search_dict = parse_answer(time_search_answer)
        if time_search_dict is None:
            return None

        # Extract time period
        time_period = time_search_dict['Time Period']
        if len(time_period) == 1:
            current_period = time_period[0]
        else:
            current_period = time_period

        # Determine if super-fine extraction is needed
        is_super_fine = (current_period[1] - current_period[0] == args.minimal_duration)

        # Configure extraction parameters
        if not is_super_fine:
            args.fine_sampling_fps = args.sampling_fps
            args.fine_short_video_frames = args.short_video_frames
        else:
            args.fine_sampling_fps = 2
            args.fine_short_video_frames = 2 * args.minimal_duration

        args.fine_memory_extract_prompt = (
                "You should explicitly and in detail describe any visible subtitles, "
                "text overlays, or voice-overs in the video. In addition: " +
                time_search_dict['Instruction']
        )

        # Generate save name
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_name = f'demo_{timestamp}'

        # Extract fine memory
        entire_memory = vlm_roles.video_fine_memory_extraction(
            vlm_model, vlm_processor, current_period, save_name, args, split="entire"
        )

        # Adjust parameters for divided extraction
        if not is_super_fine:
            args.fine_sampling_fps = 2
            args.fine_short_video_frames = 2 * args.minimal_duration
        else:
            args.fine_sampling_fps = 2
            args.fine_short_video_frames = 2

        divided_memory = vlm_roles.video_fine_memory_extraction(
            vlm_model, vlm_processor, current_period, save_name, args, split="divided"
        )

        # Store extracted memory
        memory_history = super_fine_memory_history if is_super_fine else fine_memory_history
        time_periods = memory_history['time_periods']

        if current_period in time_periods:
            idx = time_periods.index(current_period)
            memory_history['entire_memories'][idx] = entire_memory
            memory_history['divided_memories'][idx] = divided_memory
        else:
            memory_history['time_periods'].append(current_period)
            memory_history['entire_memories'].append(entire_memory)
            memory_history['divided_memories'].append(divided_memory)

        # Answer with fine memory
        fine_answer = llm_roles.video_question_answer_with_coarse_and_fine_memory(
            filtered_coarse_memory,
            fine_memory_history['entire_memories'], fine_memory_history['divided_memories'],
            super_fine_memory_history['entire_memories'], super_fine_memory_history['divided_memories'],
            question=question, options=[], args=args, client=client, duration=video_duration
        )

        fine_answer_dict = parse_answer(fine_answer)
        if fine_answer_dict is None:
            return None

        if fine_answer_dict['Confidence']:
            print("="*30)
            print(f"Question: {question}")
            print(f"Answer: {fine_answer_dict['Answer']}")
            return fine_answer_dict['Answer']

    # Phase 4: Final forced answer
    final_answer = llm_roles.video_question_must_answer_with_coarse_and_fine_memory(
        coarse_memory,
        fine_memory_history['entire_memories'], fine_memory_history['divided_memories'],
        super_fine_memory_history['entire_memories'], super_fine_memory_history['divided_memories'],
        question=question, options=[], args=args, client=client, duration=video_duration
    )

    final_answer_dict = parse_answer(final_answer)
    if final_answer_dict is None:
        return None

    print("="*30)
    print(f"Question: {question}")
    print(f"Answer: {final_answer_dict['Answer']}")
    return final_answer_dict['Answer']


if __name__ == "__main__":
    # Setup logging
    logger = Logger('videolucy_bilibili_demo.txt')
    sys.stdout = logger

    # Initialize
    args = parse_args()
    vlm_model, vlm_processor = vlm_roles.create_vlm(args)
    client = llm_roles.create_llm(args)

    # Setup directories with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    args.fine_memory_dir = f"{args.fine_memory_dir}_{timestamp}"
    args.temp_video_dir = f"{args.temp_video_dir}_{timestamp}"

    # Set video and question
    args.video_url = "https://www.bilibili.com/video/BV1Y4H6zkE1y"

    question_examples = [
        "Which restaurant did the protagonist go to for dinner in the evening? Additionally, in which year was this restaurant established, and what historical background does it have?",
        "When the protagonist was eating oysters, how many kinds of sauces were paired with them, and what were they?",
        "Where did the protagonist eat the lamb rice bowl? What did this lamb rice bowl look like, and what were its features?",
        "Where did the girl the protagonist met while eating on the street come from? What was distinctive about her clothing today?",
        "What was the previous profession of the girl the protagonist met while eating by the roadside, and what is her current occupation? What are her comments on the prospects and development of her present career?"
    ]

    # You can freely choose the question from the above examples
    question = question_examples[4]

    # Validate video source
    if (not os.path.exists(args.video_url) and
            not (args.video_url.startswith('http://') or args.video_url.startswith('https://'))):
        raise ValueError(f"Video {args.video_url} does not exist.")

    # Run inference
    answer = demo_infer(vlm_model, vlm_processor, args, question, client=client)
    print("=" * 30)