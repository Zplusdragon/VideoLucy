import sys
import re
import ast

class Logger:
    """Logger class to redirect stdout to both console and file."""

    def __init__(self, log_file_path):
        self.log_file = open(log_file_path, 'a', encoding='utf-8')
        self.original_stdout = sys.stdout

    def write(self, message):
        self.original_stdout.write(message)
        self.log_file.write(message)
        self.log_file.flush()

    def flush(self):
        self.original_stdout.flush()

    def __del__(self):
        self.log_file.close()


def parse_answer(answer_string):
    """
    Parse the answer string to extract dictionary output from LLM.

    Args:
        answer_string (str): Raw answer string from LLM

    Returns:
        dict or None: Parsed dictionary or None if parsing fails
    """
    # Extract content after </think> tag
    answer_string = answer_string.split("</think>")[-1]

    # Find all dictionary-like patterns
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, answer_string)

    if not matches:
        print(answer_string)
        print("Cannot find dictionary pattern in answer.")
        return None

    # Use the last dictionary match
    last_dict_str = matches[-1]
    last_dict_str = last_dict_str.replace("false", "False").replace("true", "True").replace("\n", "")

    try:
        parsed_dict = ast.literal_eval(last_dict_str)
        print(parsed_dict)
        return parsed_dict
    except (SyntaxError, ValueError):
        print(answer_string)
        print("Failed to parse dictionary from answer.")
        return None


def filter_coarse_memory_by_time_periods(coarse_memory, related_time_periods, overlap):
    """
    Filter coarse memory based on relevant time periods.

    Args:
        coarse_memory (list): List of coarse memory entries
        related_time_periods (list): List of relevant time periods
        overlap (float): Overlap duration in seconds

    Returns:
        list: Filtered coarse memory
    """
    last_time = coarse_memory[-1]['time_period'][1]
    duration = coarse_memory[0]['time_period'][1] - coarse_memory[0]['time_period'][0]

    # Process time periods
    processed_periods = []
    for time_period in [list(t) for t in related_time_periods]:
        if time_period != list(coarse_memory[0]['time_period']) and time_period != list(
                coarse_memory[-1]['time_period']):
            # Add surrounding periods for context
            processed_periods.extend([
                [time_period[0] + overlap - duration, time_period[0] + overlap],
                time_period,
                [time_period[1] - overlap, min(time_period[1] + duration - overlap, last_time)]
            ])
        elif time_period == list(coarse_memory[0]['time_period']):
            processed_periods.extend([
                time_period,
                [time_period[1] - overlap, min(time_period[1] + duration - overlap, last_time)]
            ])
        elif time_period == list(coarse_memory[-1]['time_period']):
            processed_periods.extend([
                [time_period[0] + overlap - duration, time_period[0] + overlap],
                time_period
            ])

    # Remove duplicates and sort
    unique_periods = set(tuple(period) for period in processed_periods)
    sorted_periods = sorted([list(period) for period in unique_periods], key=lambda x: x[0])

    # Filter coarse memory
    original_periods = [list(mem['time_period']) for mem in coarse_memory]
    filtered_memory = [mem for mem in coarse_memory if list(mem['time_period']) in sorted_periods]

    print(f"Coarse Memory Filtered with time periods: {sorted_periods}")

    # Check for missing periods
    for period in sorted_periods:
        if period not in original_periods:
            print(f"Warning: {period} not in original time periods.")

    return filtered_memory


def contains_ordinal_number(text):
    """
    Check if text contains ordinal numbers.

    Args:
        text (str): Input text

    Returns:
        bool: True if ordinal number is found
    """
    ordinal_numbers = [
        'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth',
        'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth',
        'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth',
        'twentieth', 'thirtieth', 'fortieth', 'fiftieth', 'sixtieth', 'seventieth',
        'eightieth', 'ninetieth', 'hundredth', 'last',
        '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
        '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th',
        '20th', '30th', '40th', '50th', '60th', '70th', '80th', '90th', '100th',
    ]

    return any(ordinal in text.lower() for ordinal in ordinal_numbers)