import json
from .utils import *
from volcenginesdkarkruntime import Ark

def create_llm(args):
    if args.api_call:
        print("Using LLM API:",args.api_model)
        os.environ["ARK_API_KEY"] = args.api_key
        client = Ark(
            api_key=os.environ.get("ARK_API_KEY"),
            timeout=1800
        )
        return client

    else:
        raise("Only Supporting Using LLM with API Currently!")


def coarse_memory_summarization(coarse_memory,args,client=None):
    print("-" * 20)
    print("Summarizing Coarse Memory...")
    video_path = args.video_url
    cache_dir = args.cache_dir
    video_path = get_video_path(video_path,cache_dir)
    video_path = video_path.split("VideoDataset/")[-1]
    save_name = "_".join(video_path.split(".")[0].split("/")) + "_Summarization" + ".json"

    if os.path.exists(os.path.join(cache_dir, "coarse_memory", save_name)):
        print("Coarse Memory Summarization Existed in:", os.path.join(cache_dir, "coarse_memory", save_name))
        with open(os.path.join(cache_dir, "coarse_memory", save_name), "r") as f:
            results = json.load(f)
        return results

    memory_prompt = get_summary_prompt(coarse_memory)

    if client:
        response = client.chat.completions.create(
            # 替换 <Model> 为模型的Model ID
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content

    else:
        raise ("Only Supporting Using LLM with API Currently!")

    responses = [response]
    with open(os.path.join(cache_dir, "coarse_memory",save_name), 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=4)

    return responses


def video_question_answer_with_summary(summary,question,args,client=None):
    memory_prompt = direct_answer_with_summary_prompt(summary,question)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise ("Only Supporting Using LLM with API Currently!")
    return responses[0]


def video_question_option_with_summary(summary,question,options,args,client=None):
    memory_prompt = option_answer_with_summary_prompt(summary,question,options)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise ("Only Supporting Using LLM with API Currently!")
    return responses[0]


def answer_and_options_matching_judge(question,answer,options,args,client=None):
    memory_prompt = get_answer_judge_prompt(question,answer,options)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise("Only Supporting Using LLM with API Currently!")
    return responses[0]


def video_question_answer_with_coarse_memory(coarse_memory,question,options,args,client=None):
    memory_prompt = answer_with_coarse_memory_prompt(coarse_memory,question,options)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise("Only Supporting Using LLM with API Currently!")
    return responses[0]


def video_question_answer_with_coarse_and_fine_memory(coarse_memory,entire_fine_memory_list,divided_fine_memory_list,entire_super_fine_memory_list,divided_super_fine_memory_list,question,options,args,client=None,duration=0):
    memory_prompt = answer_with_coarse_and_fine_memory_prompt(coarse_memory,entire_fine_memory_list,divided_fine_memory_list,entire_super_fine_memory_list,divided_super_fine_memory_list,question,options,duration)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise("Only Supporting Using LLM with API Currently!")
    return responses[0]


def video_question_must_answer_with_coarse_and_fine_memory(coarse_memory,entire_fine_memory_list,divided_fine_memory_list,entire_super_fine_memory_list,divided_super_fine_memory_list,question,options,args,client=None,duration=0):
    memory_prompt = must_answer_with_coarse_and_fine_memory_prompt(coarse_memory,entire_fine_memory_list,divided_fine_memory_list,entire_super_fine_memory_list,divided_super_fine_memory_list,question,options,duration)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise("Only Supporting Using LLM with API Currently!")
    return responses[0]


def video_question_get_single_related_time_with_coarse_memory(coarse_memory,entire_fine_memory_list_history,divided_fine_memory_list_history,question,options,excluded_time_periods,args,client=None,duration=0):
    memory_prompt = get_single_related_time_prompt(coarse_memory,entire_fine_memory_list_history,divided_fine_memory_list_history,question,options,excluded_time_periods,duration)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise("Only Supporting Using LLM with API Currently!")
    return responses[0]


def video_question_type_judge_with_coarse_memory(coarse_memory,question,options,args,client=None):
    memory_prompt = question_type_judge_prompt(coarse_memory,question,options)
    if client:
        response = client.chat.completions.create(
            model=args.api_model,
            messages=[
                {"role": "user", "content": memory_prompt}
            ],
            thinking={
                "type": args.thinking
            }
        )
        response = response.choices[0].message.content
        responses = [response]
    else:
        raise("Only Supporting Using LLM with API Currently!")
    return responses[0]