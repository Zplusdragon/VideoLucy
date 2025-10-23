import hashlib
from decord import VideoReader, cpu
import cv2
import os
import subprocess

def download_bilibili_video(url, dest_path):
    if '.mp4' in dest_path:
        dest_path = dest_path.split('.mp4')[0]
    print("Downloading:", url)
    try:
        command = f'you-get -o {os.path.dirname(dest_path)} -O {os.path.basename(dest_path)} {url}'
        result = subprocess.run(command, shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Video downloaded to {dest_path}")
    except subprocess.CalledProcessError as e:
        print(f"执行命令时出现错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


def get_video_path(video_path,cache_dir: str = 'cache'):
    video_hash = hashlib.md5(video_path.encode('utf-8')).hexdigest()
    if video_path.startswith('http://') or video_path.startswith('https://'):
        video_file_path = os.path.join(cache_dir, f'{video_hash}.mp4')
        if not os.path.exists(video_file_path):
            download_bilibili_video(video_path, video_file_path)
    else:
        video_file_path = video_path
    return video_file_path


def get_video_frames(video_path, cache_dir: str = 'cache', frames_per_second: float = 1.0,
                     short_video_frames: int = 100, time_period= None, overlapping_frames:int=0,temp_video_dir:str='temp_videos'):
    # 确保 frames_per_second 大于 0
    assert frames_per_second > 0, "frames_per_second 必须大于 0"
    # 确保 short_video_frames 是正整数

    assert isinstance(short_video_frames, int) and short_video_frames > 0, "short_video_frames 必须是正整数"
    if time_period:
        assert len(time_period) == 2 and time_period[0] < time_period[1], "time_period 必须是一个包含两个元素的元组，且第一个元素小于第二个元素"
    # 确保 overlapping_frames 是非负整数
    assert isinstance(overlapping_frames, int) and overlapping_frames >= 0, "overlapping_frames 必须是非负整数"

    video_file_path = video_path
    vr = VideoReader(video_file_path, ctx=cpu(0))
    fps = vr.get_avg_fps()
    total_frames = len(vr)
    total_seconds = total_frames / fps

    # 根据 time_period 确定子视频的起始和结束帧
    if time_period:
        start_time, end_time = time_period
        start_frame = int(start_time * fps)
        end_frame = min(int(end_time * fps), total_frames)
    else:
        start_frame = 0
        end_frame = total_frames

    all_frames = []
    interval = 1 / frames_per_second  # 计算抽帧间隔（秒）
    current_time = start_time if time_period else 0
    while current_time < (end_time if time_period else total_seconds):
        frame_index = int(current_time * fps)
        if start_frame <= frame_index < end_frame:
            all_frames.append(vr[frame_index].asnumpy())
        current_time += interval

    print("Original Video Frames:", total_frames)
    print("Original Video Seconds:", total_seconds)
    print("Sampling FPS:", frames_per_second)

    if 0 < len(all_frames) % short_video_frames <= frames_per_second:
        all_frames = all_frames[:len(all_frames)-len(all_frames) % short_video_frames]

    print("Sampled Video Frames:", len(all_frames))

    # 每 short_video_frames 帧构成一个短视频，考虑重叠帧数
    short_video_paths = []
    short_video_time_ranges = []
    i = 0
    while i < len(all_frames):
        end_index = min(i + short_video_frames, len(all_frames))
        short_video = all_frames[i: end_index]
        if short_video:
            if time_period:
                start_time = start_frame / fps + i / frames_per_second
                end_time = start_frame / fps + (i + len(short_video)) / frames_per_second
            else:
                start_time = i / frames_per_second
                end_time = (i + len(short_video)) / frames_per_second
            short_video_time_ranges.append((start_time, end_time))
            temp_video_path = os.path.join(cache_dir, temp_video_dir, f'temp_video_{len(short_video_paths)}.mp4')
            height, width, layers = short_video[0].shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, frames_per_second, (width, height))
            for frame in short_video:
                # 将 RGB 转换为 BGR
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(bgr_frame)
            out.release()
            short_video_paths.append(temp_video_path)

        if end_index == len(all_frames):
            break
        i = max(i + 1, end_index - overlapping_frames)

    print("Each Short Video Frames:", short_video_frames)
    print('Short Video Numbers:', len(short_video_paths))
    return short_video_paths, short_video_time_ranges