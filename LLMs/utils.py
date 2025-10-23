import copy
import os
import hashlib

def get_video_path(video_path,cache_dir: str = 'cache'):
    video_hash = hashlib.md5(video_path.encode('utf-8')).hexdigest()
    if video_path.startswith('http://') or video_path.startswith('https://'):
        video_file_path = os.path.join(cache_dir, f'{video_hash}.mp4')
    else:
        video_file_path = video_path
    return video_file_path

def answer_with_coarse_memory_prompt(memory:list,question:str,options:list):
    memory_prompt = "The following provides a rough description of what's shown in the video during different time periods:\n"
    for i, mem in enumerate(memory):
        caption = mem['general_memory']
        start_time = mem['time_period'][0]
        end_time = mem['time_period'][1]
        time_period = 'from {}s to {}s. '.format(start_time,end_time)
        memory_prompt = memory_prompt + str(i+1) + ". Time Period: " + time_period + "Content Description: "+caption + "\n\n"
    memory_prompt = memory_prompt + "Note that since these descriptions are not very complete and detailed, some key information in the video segments of each time period may not all appear in these content descriptions. \n"

    memory_prompt = memory_prompt + "Now, a question has been raised regarding the content descriptions of this video.\n" + question + "\n"
    for opt in options:
        memory_prompt = memory_prompt + opt + '\n'

    memory_prompt = memory_prompt + "Please read the given video content descriptions and the question in depth, and determine whether you can accurately answer the given question solely based on the currently provided descriptions.\n"

    memory_prompt = memory_prompt + "If you can answer it with absolute confidence, please answer this question and provide the time periods you are referring to. The answer you provide must have completely and absolutely objective support in the video descriptions. Do not make inferences arbitrarily.\n"

    if len(options)!=0:
        memory_prompt = memory_prompt + "Please note that there is only one option that can answer this question. The answer you provide must include the English letters of the options [A, B, C, D]. \n"

    memory_prompt = memory_prompt + "If you think the current content descriptions of the video is still insufficient to accurately answer the question, please do not answer it and give me your reason.\n"
    memory_prompt = memory_prompt + "Please output in a strictly standardized dictionary format containing four key-value pairs:\n"
    memory_prompt = memory_prompt + '"Confidence": A boolean value. Set it to True if you are certain about the answer, and False if not.\n'
    memory_prompt = memory_prompt + '"Answer": A string. This string must be enclosed in double quotes. When "Confidence" is True, fill in the answer content; when "Confidence" is False, fill in "No Answer".\n'
    memory_prompt = memory_prompt + '"Time Period": A list. When "Confidence" is True, fill in the list with time periods corresponding to the answer, each in the format of a tuple (start time, end time); when "Confidence" is False, fill in "No Time".\n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasoning about your judgment. You need to ensure and check that your reasoning must be able to absolutely support your answer. \n'
    memory_prompt = memory_prompt + "Note that no additional comments should be added within the dictionary."
    memory_prompt = memory_prompt + "You must note that if an ordinal number appears in the provided question, in the vast majority of cases, you should not simply assume that this ordinal number represents the ordinal of the provided time period. You need to focus on understanding the specific meaning of this ordinal number within the question based on all the content descriptions. \n"
    return memory_prompt



def get_summary_prompt(coarse_memory:list):
    memory_prompt = "The following provides a description of what's shown in the video during different time periods.\n"
    for i, mem in enumerate(coarse_memory):
        caption = mem['general_memory']
        start_time = mem['time_period'][0]
        end_time = mem['time_period'][1]
        time_period = 'from {}s to {}s. '.format(start_time, end_time)
        memory_prompt = memory_prompt + str(
            i + 1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n\n"
    memory_prompt = memory_prompt + "Please think about and understand the main content and theme of this video based on the descriptions of these different time periods. According to the theme of the video, please write a comprehensive introduction to the video content that best highlights this theme. The introduction should be presented in a sequential narrative form, with concise and clear content, natural transitions between each part, and demonstrate the core content and development process of the video from beginning to end. \n"
    return memory_prompt


def direct_answer_with_summary_prompt(summary:list,question:str):
    memory_prompt = "The following presents a rough description of the content of a video from beginning to end:\n"
    memory_prompt = memory_prompt + summary[0] + '\n\n'
    memory_prompt = memory_prompt + "Note that since this description is not very complete and detailed, some key information in this video may not all appear in it. \n"

    memory_prompt = memory_prompt + "Now, a question has been raised regarding this video.\n" + question + "\n"
    memory_prompt = memory_prompt + "Read the given video content descriptions and the question in depth, and determine whether you can answer the given question with absolute and complete confidence.\n"
    memory_prompt = memory_prompt + "If you can answer it with absolute and complete confidence, please answer this question directly and give me your reason.\n"
    memory_prompt = memory_prompt + "If you think the current content descriptions of the video is still insufficient to accurately answer the question, please also give me your reason.\n"
    memory_prompt = memory_prompt + "Note that the answer you provide must be supported by absolute objective evidence in the descriptions. Do not make unfounded inferences without evidence.\n"
    memory_prompt = memory_prompt + "Your provided answer should be as concise and easy to understand as possible. \n"
    memory_prompt = memory_prompt + "Please output in a strictly standardized dictionary format containing three key-value pairs:\n"
    memory_prompt = memory_prompt + '"Confidence": A boolean value. Set it to True if you are certain about the answer, and False if not.\n'
    memory_prompt = memory_prompt + '"Answer": A string. This string must be enclosed in double quotes. When "Confidence" is True, fill in the answer content; when "Confidence" is False, fill in "No Answer".\n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasoning about your judgment. You need to ensure and check that your reasoning must be able to absolutely support your answer. \n'
    memory_prompt = memory_prompt + "No additional comments should be added within the dictionary."
    return memory_prompt


def option_answer_with_summary_prompt(summary:list,question:str,options:list):
    memory_prompt = "The following presents a rough description of the content of a video from beginning to end:\n"
    memory_prompt = memory_prompt + summary[0] + '\n\n'
    memory_prompt = memory_prompt + "Note that since this description is not very complete and detailed, some key information in this video may not all appear in it. \n"

    memory_prompt = memory_prompt + "Now, a question has been raised regarding this video.\n" + question + "\n"
    for opt in options:
        memory_prompt = memory_prompt + opt + '\n'
    memory_prompt = memory_prompt + "Read the given video content descriptions and the question in depth, and determine whether you can answer the given question with absolute and complete confidence.\n"
    memory_prompt = memory_prompt + "If you can answer it with absolute and complete confidence, please answer this question and give me your reason. The answer you provide must be a single option and include the English letters of the options [A, B, C, D]. \n"
    memory_prompt = memory_prompt + "If you think the current content descriptions of the video is still insufficient to accurately answer the question, please also give me your reason.\n"
    memory_prompt = memory_prompt + "Note that the answer you provide must be supported by absolute objective evidence in the descriptions. Do not make unfounded inferences without evidence.\n"
    memory_prompt = memory_prompt + "Please note that there is only one option that can best answer this question. \n"
    memory_prompt = memory_prompt + "Please output in a strictly standardized dictionary format containing three key-value pairs:\n"
    memory_prompt = memory_prompt + '"Confidence": A boolean value. Set it to True if you are certain about the answer, and False if not.\n'
    memory_prompt = memory_prompt + '"Answer": A string. This string must be enclosed in double quotes. When "Confidence" is True, fill in the answer content; when "Confidence" is False, fill in "No Answer".\n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasoning about your judgment. You need to ensure and check that your reasoning must be able to absolutely support your answer. \n'
    memory_prompt = memory_prompt + "No additional comments should be added within the dictionary."
    return memory_prompt



def answer_with_coarse_and_fine_memory_prompt(coarse_memory:list,entire_fine_memory_list:list,divided_fine_memory_list:list,entire_super_fine_memory_list:list,divided_super_fine_memory_list:list,question:str,options:list,duration:int):
    coarse_memory_copy = copy.deepcopy(coarse_memory)
    fine_memory_time_period_list = []
    super_fine_memory_time_period_list = []

    for fine_memory in entire_fine_memory_list:
        start_time = fine_memory[0]['time_period'][0]
        end_time = fine_memory[-1]['time_period'][1]
        fine_memory_time_period_list.append([start_time,end_time])

    for super_fine_memory in entire_super_fine_memory_list:
        start_time = super_fine_memory[0]['time_period'][0]
        end_time = super_fine_memory[-1]['time_period'][1]
        super_fine_memory_time_period_list.append([start_time,end_time])

    coarse_memory_copy_saved = []
    for mem in coarse_memory_copy:
        time_period = list(mem['time_period'])
        if time_period not in fine_memory_time_period_list:
            coarse_memory_copy_saved.append(mem)

    total_memories = coarse_memory_copy_saved

    for fine_memory in entire_fine_memory_list:
        total_memories += fine_memory

    total_memories = sorted(total_memories, key=lambda x: x['time_period'][0])
    memory_prompt = "There is currently a video with a total duration of {} seconds.\n".format(duration)
    memory_prompt = memory_prompt+"The following gives a general description of what is shown in the video during certain time periods:\n"
    for i, mem in enumerate(total_memories):
        caption = mem['general_memory']
        start_time = mem['time_period'][0]
        end_time = mem['time_period'][1]
        time_period = 'from {}s to {}s. '.format(start_time, end_time)
        memory_prompt = memory_prompt + str(i + 1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n\n"
        if [start_time,end_time] in fine_memory_time_period_list:
            idx = fine_memory_time_period_list.index([start_time,end_time])
            divided_mems = divided_fine_memory_list[idx]
            memory_prompt = memory_prompt + "Note that for the video within this time period from {} seconds to {} seconds, there is the following more detailed description:\n".format(start_time,end_time)
            for j, divided_mem in enumerate(divided_mems):
                caption = divided_mem['general_memory']
                start_time = divided_mem['time_period'][0]
                end_time = divided_mem['time_period'][1]
                time_period = 'from {}s to {}s. '.format(start_time, end_time)

                if [start_time,end_time] not in super_fine_memory_time_period_list:
                    memory_prompt = memory_prompt + "    ({})".format(j+1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n"
                else:
                    idx = super_fine_memory_time_period_list.index([start_time, end_time])
                    divided_mems = divided_super_fine_memory_list[idx]
                    memory_prompt = memory_prompt + "    ({})".format(j + 1) + ". Time Period: " + time_period + "Content Description: " + entire_super_fine_memory_list[idx][0]['general_memory'] + "\n"

                    memory_prompt = memory_prompt + "Note that for the video within this time period from {} seconds to {} seconds, there is the following more detailed description:\n".format(
                        start_time, end_time)
                    for k, divided_mem in enumerate(divided_mems):
                        caption = divided_mem['general_memory']
                        start_time = divided_mem['time_period'][0]
                        end_time = divided_mem['time_period'][1]
                        memory_prompt = memory_prompt + "    [{}]".format(k + 1) + ". Time Stamp: " + "{}s. ".format(start_time) + "Content Description: " + caption + "\n"
    memory_prompt = memory_prompt + "Now, a question has been raised regarding the content descriptions of this video.\n" + question + "\n"
    for opt in options:
        memory_prompt = memory_prompt + opt + '\n'

    memory_prompt = memory_prompt + "Please read the given video content descriptions and the question in depth, and determine whether you can accurately answer the given question solely based on the currently provided descriptions.\n"

    memory_prompt = memory_prompt + "If you can answer it with absolute confidence, please answer this question and provide the time periods of the video content you are referring to. The answer you provide must have completely and absolutely objective support in the video descriptions. Do not make inferences arbitrarily.\n"

    if len(options) != 0:
        memory_prompt = memory_prompt + "Please note that there is only one option that can answer this question. The answer you provide must include the English letters of the options [A, B, C, D]. \n"

    memory_prompt = memory_prompt + "If you think the current content descriptions of the video are still insufficient to accurately answer the question, please do not answer it and give me your reason.\n"

    memory_prompt = memory_prompt + "Please output in a strictly standardized dictionary format containing four key-value pairs:\n"
    memory_prompt = memory_prompt + '"Confidence": A boolean value. Set it to True if you are certain about the answer, and False if not.\n'
    memory_prompt = memory_prompt + '"Answer": A string. This string must be enclosed in double quotes. When "Confidence" is True, fill in the answer content; when "Confidence" is False, fill in "No Answer".\n'
    memory_prompt = memory_prompt + '"Time Period": A list. When "Confidence" is True, fill in the list with time periods corresponding to the answer, each in the format of a tuple (start time, end time); when "Confidence" is False, fill in "No Time".\n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasoning about your judgment. You need to ensure and check that your reasoning must be able to absolutely support your answer. \n'
    memory_prompt = memory_prompt + "No additional comments should be added within the dictionary."
    memory_prompt = memory_prompt + "You must note that if an ordinal number appears in the provided question, in the vast majority of cases, you should not simply assume that this ordinal number represents the ordinal of the provided time period. You need to focus on understanding the specific meaning of this ordinal number within the question based on all the content descriptions. \n"
    return memory_prompt



def must_answer_with_coarse_and_fine_memory_prompt(coarse_memory:list,entire_fine_memory_list:list,divided_fine_memory_list:list,entire_super_fine_memory_list:list,divided_super_fine_memory_list:list,question:str,options:list,duration:int):
    coarse_memory_copy = copy.deepcopy(coarse_memory)
    fine_memory_time_period_list = []
    super_fine_memory_time_period_list = []

    for fine_memory in entire_fine_memory_list:
        start_time = fine_memory[0]['time_period'][0]
        end_time = fine_memory[-1]['time_period'][1]
        fine_memory_time_period_list.append([start_time, end_time])

    for super_fine_memory in entire_super_fine_memory_list:
        start_time = super_fine_memory[0]['time_period'][0]
        end_time = super_fine_memory[-1]['time_period'][1]
        super_fine_memory_time_period_list.append([start_time, end_time])

    coarse_memory_copy_saved = []
    for mem in coarse_memory_copy:
        time_period = list(mem['time_period'])
        if time_period not in fine_memory_time_period_list:
            coarse_memory_copy_saved.append(mem)

    total_memories = coarse_memory_copy_saved

    for fine_memory in entire_fine_memory_list:
        total_memories += fine_memory

    total_memories = sorted(total_memories, key=lambda x: x['time_period'][0])
    memory_prompt = "There is currently a video with a total duration of {} seconds.\n".format(duration)
    memory_prompt = memory_prompt + "The following gives a general description of what is shown in the video during certain time periods:\n"
    for i, mem in enumerate(total_memories):
        caption = mem['general_memory']
        start_time = mem['time_period'][0]
        end_time = mem['time_period'][1]
        time_period = 'from {}s to {}s. '.format(start_time, end_time)
        memory_prompt = memory_prompt + str(
            i + 1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n\n"
        if [start_time, end_time] in fine_memory_time_period_list:
            idx = fine_memory_time_period_list.index([start_time, end_time])
            divided_mems = divided_fine_memory_list[idx]
            memory_prompt = memory_prompt + "Note that for the video within this time period from {} seconds to {} seconds, there is the following more detailed and accurate description:\n".format(
                start_time, end_time)
            for j, divided_mem in enumerate(divided_mems):
                caption = divided_mem['general_memory']
                start_time = divided_mem['time_period'][0]
                end_time = divided_mem['time_period'][1]
                time_period = 'from {}s to {}s. '.format(start_time, end_time)

                if [start_time, end_time] not in super_fine_memory_time_period_list:
                    memory_prompt = memory_prompt + "    ({})".format(
                        j + 1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n"
                else:
                    idx = super_fine_memory_time_period_list.index([start_time, end_time])
                    divided_mems = divided_super_fine_memory_list[idx]
                    memory_prompt = memory_prompt + "    ({})".format(
                        j + 1) + ". Time Period: " + time_period + "Content Description: " + \
                                    entire_super_fine_memory_list[idx][0]['general_memory'] + "\n"

                    memory_prompt = memory_prompt + "Note that for the video within this time period from {} seconds to {} seconds, there is the following more detailed and accurate description:\n".format(
                        start_time, end_time)
                    for k, divided_mem in enumerate(divided_mems):
                        caption = divided_mem['general_memory']
                        start_time = divided_mem['time_period'][0]
                        end_time = divided_mem['time_period'][1]
                        memory_prompt = memory_prompt + "    [{}]".format(
                            k + 1) + ". Time Stamp: " + "{}s. ".format(start_time) + "Content Description: " + caption + "\n"

    memory_prompt = memory_prompt + "Now, a question has been raised regarding the content descriptions of this video.\n" + question + "\n"

    for opt in options:
        memory_prompt = memory_prompt + opt + '\n'

    memory_prompt = memory_prompt + "Please read and understand the given video content and question in depth. "

    if len(options) != 0:
        memory_prompt = memory_prompt + "Strictly based on the video content, select the single best option. You must choose an option from these provided options. The answer you provide must include the English letters of the options [A, B, C, D]. \n"
    else:
        memory_prompt = memory_prompt + "You must provide a best answer for this question.\n"

    memory_prompt = memory_prompt + "Please note that if an ordinal number appears in the provided question, in most cases, the meaning of this ordinal number is not related to the ordinal of the provided time period. You need to focus on analyzing the meaning of this ordinal number. \n"
    memory_prompt = memory_prompt + "Please output in a strictly standardized dictionary format containing three key-value pair:\n"
    memory_prompt = memory_prompt + '"Answer": A string. This string must be enclosed in double quotes. The best answer for the question.\n'
    memory_prompt = memory_prompt + '"Time Period": A list. Fill in the list with time periods corresponding to the best answer, each in the format of a tuple (start time, end time).\n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasoning about your judgment. You need to ensure and check that your reasoning must be able to absolutely support your answer. \n'
    memory_prompt = memory_prompt + "No additional comments should be added within the dictionary."
    return memory_prompt


def get_answer_judge_prompt(question:str,direct_answer:str,options:list):
    prompt = "Now a question is given:\n"
    prompt = prompt + question + '\n'
    prompt = prompt + "The best answer to this question comes from one of the following options:\n"
    for opt in options:
        prompt = prompt + opt + '\n'
    prompt = prompt + "There is now a model that has provided a direct answer to this question, and its answer is:\n"
    prompt = prompt + direct_answer
    prompt = prompt + "Please determine which one of the above options the direct answer from the model corresponds to.\n"
    prompt = prompt + "When making the judgment, please base it on whether the core concept described in the options is included in the model's answer.\n"
    prompt = prompt + "If the key information mentioned in the model's answer is consistent with or highly similar to the information in a certain option, consider the answer correct and provide the matching option. If it corresponds to none of the options or appears to correspond to multiple options, indicate that the answer is incorrect, that is, there is no matching option.\n"
    prompt = prompt + "Please provide your judgment result and explain in detail the reasons for your judgment.\n"
    prompt = prompt + "Your output must be in a strictly standardized dictionary format containing three key-value pair:\n"
    prompt = prompt + '"Matching": A boolean value. If you are quite confident that the direct answer of the model can correspond to a certain option, set it as True. Otherwise, set it as False. \n'
    prompt = prompt + '"Option": A string. This string must be enclosed in double quotes. If "Matching" is True, then provide the original option that the direct answer corresponds to. The answer you provide must include the English letters of the options [A, B, C, D]. If "Matching" is False, fill in "No matched option.".\n'
    prompt = prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasoning about your judgment. You need to ensure and check that your reasoning must be able to absolutely support your answer. \n'
    prompt = prompt + "No additional comments should be added within the dictionary."
    return prompt


def get_single_related_time_prompt(coarse_memory:list,entire_fine_memory_list:list,divided_fine_memory_list:list,question:str,options:list,excluded_periods:list,duration:float):
    coarse_memory_copy = copy.deepcopy(coarse_memory)
    fine_memory_time_period_list = []

    for fine_memory in entire_fine_memory_list:
        start_time = fine_memory[0]['time_period'][0]
        end_time = fine_memory[-1]['time_period'][1]
        fine_memory_time_period_list.append([start_time, end_time])

    coarse_memory_copy_saved = []
    for mem in coarse_memory_copy:
        time_period = list(mem['time_period'])
        if time_period not in fine_memory_time_period_list:
            coarse_memory_copy_saved.append(mem)

    total_memories = coarse_memory_copy_saved

    for fine_memory in entire_fine_memory_list:
        total_memories += fine_memory

    total_memories = sorted(total_memories, key=lambda x: x['time_period'][0])
    memory_prompt = "There is currently a video with a total duration of {} seconds.\n".format(duration)
    memory_prompt = memory_prompt + "The following gives a general description of what is shown in the video during certain time periods:\n"
    for i, mem in enumerate(total_memories):
        caption = mem['general_memory']
        start_time = mem['time_period'][0]
        end_time = mem['time_period'][1]
        time_period = 'from {}s to {}s. '.format(start_time, end_time)
        memory_prompt = memory_prompt + str(
            i + 1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n\n"
        # memory_prompt = memory_prompt + "Time Period: " + time_period + "Content Description: " + caption + "\n\n"
        if [start_time, end_time] in fine_memory_time_period_list:
            idx = fine_memory_time_period_list.index([start_time, end_time])
            divided_mems = divided_fine_memory_list[idx]
            memory_prompt = memory_prompt + "Note that for the video within this time period from {} seconds to {} seconds, there is the following more detailed description:\n".format(
                start_time, end_time)
            for j, divided_mem in enumerate(divided_mems):
                caption = divided_mem['general_memory']
                start_time = divided_mem['time_period'][0]
                end_time = divided_mem['time_period'][1]
                time_period = 'from {}s to {}s. '.format(start_time, end_time)
                memory_prompt = memory_prompt + "    ({})".format(
                    j + 1) + ". Time Period: " + time_period + "Content Description: " + caption + "\n"

    memory_prompt = memory_prompt + "Now, a question has been raised regarding this entire video which has a duration of {} seconds.\n".format(duration) + question + "\n"
    for opt in options:
        memory_prompt = memory_prompt + opt + '\n'
    memory_prompt = memory_prompt + "Please read the given video content descriptions and the question in depth.\n"
    memory_prompt = memory_prompt + "You do not need to answer this question.\n"

    memory_prompt = memory_prompt + "Your first task is to identify, based on the video content in each time period, the single time period that is most relevant to the question and that you think requires further elaboration of its video content details to make the answer to this question more explicit.\n"

    if len(excluded_periods)!=0:
        memory_prompt = memory_prompt + "Notably, you only need to select the most relevant one from the time periods other than the following time periods:\n"
        for period in excluded_periods:
            memory_prompt = memory_prompt +"({},{});\n".format(period[0],period[1])

    memory_prompt = memory_prompt + "In addition, assume there is now a caption model that can describe a given video according to your instruction.\n"
    memory_prompt = memory_prompt +  "Your second task is to consider what detailed content in the video of the time period you have selected you want the model to focus on describing, and provide your instruction.\n"
    memory_prompt = memory_prompt + "For example, assume that the entire video segment is about an offensive play in a certain football game, and you want to focus on the passing situation of the football during this offensive play. The instruction you give to the model could be:\n"
    memory_prompt = memory_prompt + "Please observe all the details in this video very carefully and provide a detailed and objective description of what is shown in the video. If this video is about an offensive play in a football match, you should focus particularly on the passing situation of the football during this offensive play. \n"

    memory_prompt = memory_prompt + "Note that you should organize your instruction by strictly referring to the language expressions in the above example.\n"

    memory_prompt = memory_prompt + "You should output in a strictly standardized dictionary format containing three key-value pairs:\n"
    memory_prompt = memory_prompt + '"Time Period": A list. Fill in the list with the single most relevant time period, in the tuple format (start time, end time).\n'
    memory_prompt = memory_prompt + '"Instruction": A String. This string must be enclosed in double quotes. Show me the instruction you want to give to the caption model for the second task. \n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasons for the time period and instruction you provided.\n'
    memory_prompt = memory_prompt + "No additional comments should be added within the dictionary."
    memory_prompt = memory_prompt + "You must note that if an ordinal number appears in the provided question, in the vast majority of cases, you should not simply assume that this ordinal number represents the ordinal of the provided time period. You need to focus on understanding the specific meaning of this ordinal number within the question based on all the content descriptions. \n"
    return memory_prompt


def question_type_judge_prompt(memory:list,question:str,options:list):
    memory_prompt = "The following provides a rough description of what's shown in the video during different time periods:\n"
    for i, mem in enumerate(memory):
        caption = mem['general_memory']
        start_time = mem['time_period'][0]
        end_time = mem['time_period'][1]
        time_period = 'from {}s to {}s. '.format(start_time,end_time)
        memory_prompt = memory_prompt + str(i+1) + ". Time Period: " + time_period + "Content Description: "+caption + "\n\n"
        #memory_prompt = memory_prompt + "Time Period: " + time_period + "Content Description: " + caption + "\n\n"
    memory_prompt = memory_prompt + "Now, a question has been raised regarding this video.\n" + question + "\n"
    for opt in options:
        memory_prompt = memory_prompt + opt + '\n'

    memory_prompt = memory_prompt + "Please read the given video content descriptions and the question in depth.\n"

    memory_prompt = memory_prompt + "Since most of these descriptions are rather rough and some detailed information is lost, my task is to try my best to find the time periods related to the given question, and then provide more detailed descriptions of the video content of these time periods. \n"
    memory_prompt = memory_prompt + "In order to assist me in completing my task, your task is to:\n"
    memory_prompt = memory_prompt + "Based on the provided rough video descriptions, determine whether the given question allows me to provide a more confident answer by further observing the video content of two time periods. \n"
    memory_prompt = memory_prompt + "If so, you should find out the time periods related to the question as much as possible and provide these relevant time periods so that I can review the content information of these video segments again to obtain more information and answer the question better.\n"

    memory_prompt = memory_prompt + "For example, since there is no need for an overall understanding of large video segments, the following questions can obtain more accurate answers by carefully re-observing the video segments of two time periods:\n"
    memory_prompt = memory_prompt + "(i) What color is Putin's tie between the interview with Antony Blinkoen and interview with Marie Yovanovitch?\n"
    memory_prompt = memory_prompt + "(ii) How does the goalkeeper prevent Liverpool's shot from scoring at 81:38 in the video?\n"
    memory_prompt = memory_prompt + "(iii) Who smashes the magic mirror?\n"

    memory_prompt = memory_prompt + "On the contrary, for example, because an overall understanding of large video segments is required, it is difficult to obtain more accurate answers to the following questions by merely observing two video segments:\n"
    memory_prompt = memory_prompt + "(i) What happens in the second half of the game?\n"
    memory_prompt = memory_prompt + "(ii) What is the video about?\n"
    memory_prompt = memory_prompt + "(iii) Which places has the protagonist of this video been to in total?\n"

    memory_prompt = memory_prompt + "You should output in a strictly standardized dictionary format containing three key-value pairs:\n"
    memory_prompt = memory_prompt + '"Flag": A bool. If you are very confident that you can provide the time periods according to the above requirements, set it as True. Otherwise, set it as False. \n'
    memory_prompt = memory_prompt + '"Time Period": A list. If "Flag" is True, fill in the list with the most relevant two time periods, in the tuple format (start time, end time). If "Flag" is False, fill in "No Time Periods."\n'
    memory_prompt = memory_prompt + '"Reason": A String. This string must be enclosed in double quotes. Show me your reasons for the time periods you provided.\n'
    memory_prompt = memory_prompt + "No additional comments should be added within the dictionary."

    return memory_prompt