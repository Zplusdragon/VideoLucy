import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import json
from .utils import *


def create_vlm(args):
    model_path = args.vlm_model_path

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map = "auto"
    )

    processor = AutoProcessor.from_pretrained(model_path)
    processor.tokenizer.padding_side = 'left'
    return model, processor


def video_coarse_memory_extraction(model,processor,args):
    print("-" * 20)
    print("Coarse Memory Extracting...")
    video_url = args.video_url
    prompt = args.coarse_memory_extract_prompt
    cache_dir = args.cache_dir
    batch_size = args.infer_batch_size
    frames_per_second = args.sampling_fps
    short_video_frames = args.short_video_frames
    max_pixels = args.coarse_memory_max_pixels
    overlapping_frames = args.coarse_overlapping_frames
    temp_video_dir = args.temp_video_dir

    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(os.path.join(cache_dir, temp_video_dir), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, "coarse_memory"), exist_ok=True)

    video_path = get_video_path(video_url,cache_dir)

    save_name = "_".join(video_path.split("VideoDataset/")[-1].split(".")[0].split("/")) + ".json"
    # 如果记忆存在，则直接返回记忆
    if os.path.exists(os.path.join(cache_dir, "coarse_memory", save_name)):
        print("Coarse Memory Existed in:", os.path.join(cache_dir, "coarse_memory", save_name))
        with open(os.path.join(cache_dir, "coarse_memory", save_name), "r") as f:
            results = json.load(f)
        print("-" * 20)
        return results

    short_video_paths, short_video_time_ranges = get_video_frames(video_path, cache_dir, frames_per_second,
                                                                              short_video_frames,overlapping_frames=overlapping_frames,temp_video_dir=temp_video_dir)


    # 批量推理
    all_output_texts = []
    for i in range(0, len(short_video_paths), batch_size):
        batch_short_video_paths = short_video_paths[i: i + batch_size]
        messages = []

        for j, short_video_path in enumerate(batch_short_video_paths):
            message = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"video": short_video_path, "total_pixels": 128000 * 28 * 28 * 0.9, "min_pixels": 16 * 28 * 28,
                     "max_pixels": max_pixels, 'fps': frames_per_second},
                ]}
            ]
            messages.append(message)

        texts = [
            processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
            for msg in messages
        ]
        image_inputs, video_inputs, video_kwargs = process_vision_info(messages, return_video_kwargs=True)
        fps_inputs = video_kwargs['fps']
        inputs = processor(
            text=texts,
            images=image_inputs,
            videos=video_inputs,
            fps=fps_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        generated_ids = model.generate(**inputs, max_new_tokens=2048)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_texts = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )

        for j, output_text in enumerate(output_texts):
            print(f"Short Video {i + j} Coarse Memory Extracted")
            all_output_texts.append(output_text)

    results = []
    for output_text, time_range in zip(all_output_texts, short_video_time_ranges):
        result = {
            "time_period": (round(time_range[0],1),round(time_range[1],1)),
            "general_memory": output_text
        }
        results.append(result)

    with open(os.path.join(cache_dir, "coarse_memory",save_name), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("-" * 20)
    return results


def video_fine_memory_extraction(model,processor,time_period,qid,args,split='entire'):
    print("-" * 20)
    print("Fine Memory Extracting...")
    video_url = args.video_url
    prompt = args.fine_memory_extract_prompt
    cache_dir = args.cache_dir
    batch_size = args.infer_batch_size
    frames_per_second = args.fine_sampling_fps
    short_video_frames = args.fine_short_video_frames
    max_pixels = args.fine_memory_max_pixels
    fine_memory_dir = args.fine_memory_dir
    temp_video_dir = args.temp_video_dir
    overlapping_frames = args.fine_overlapping_frames

    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(os.path.join(cache_dir, temp_video_dir), exist_ok=True)
    os.makedirs(os.path.join(cache_dir, fine_memory_dir), exist_ok=True)

    video_path = get_video_path(video_url, cache_dir)

    save_name = "{}s_{}s_".format(time_period[0], time_period[1]) + "_".join(
        video_path.split("VideoDataset/")[-1].split(".")[0].split("/")) +"_" + str(qid) + '_'+split+".json"

    short_video_paths, short_video_time_ranges = get_video_frames(video_path, cache_dir, frames_per_second,
                                                                              short_video_frames,time_period,overlapping_frames,temp_video_dir=temp_video_dir)

    # 批量推理
    all_output_texts = []
    for i in range(0, len(short_video_paths), batch_size):
        batch_short_video_paths = short_video_paths[i: i + batch_size]
        messages = []

        for j, short_video_path in enumerate(batch_short_video_paths):
            message = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"video": short_video_path, "total_pixels": 128000 * 28 * 28 * 0.9, "min_pixels": 16 * 28 * 28,
                     "max_pixels": max_pixels, 'fps': frames_per_second},
                ]}
            ]
            messages.append(message)

        texts = [
            processor.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
            for msg in messages
        ]
        image_inputs, video_inputs, video_kwargs = process_vision_info(messages, return_video_kwargs=True)
        fps_inputs = video_kwargs['fps']
        inputs = processor(
            text=texts,
            images=image_inputs,
            videos=video_inputs,
            fps=fps_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        generated_ids = model.generate(**inputs, max_new_tokens=2048)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_texts = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )

        for j, output_text in enumerate(output_texts):
            print(f"Short Video {i + j} Fine Memory Extracted")
            all_output_texts.append(output_text)

    results = []
    for output_text, time_range in zip(all_output_texts, short_video_time_ranges):
        result = {
            "time_period": (round(time_range[0],1),round(time_range[1],1)),
            "general_memory": output_text
        }
        results.append(result)

    with open(os.path.join(cache_dir, fine_memory_dir,save_name), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("-" * 20)
    return results
