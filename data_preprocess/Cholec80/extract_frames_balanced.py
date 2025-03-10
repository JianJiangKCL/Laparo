import cv2
import os
from concurrent.futures import ThreadPoolExecutor

def read_phase_info(count_file):
    phase_info = {}
    with open(count_file, 'r') as f:
        current_video = None
        phases = {}
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.endswith('-phase:'):
                if current_video is not None:
                    phase_info[current_video] = phases
                current_video = line.replace('-phase:', '')
                phases = {}
            else:
                phase_name, frame_range = line.split(': ')
                start, end = map(int, frame_range.split('-'))
                phases[phase_name] = (start, end)
        if current_video is not None:
            phase_info[current_video] = phases
    return phase_info

def get_frame_interval(phase_name):
    # 返回每个阶段的抽帧间隔（秒）为了样本均匀分布
    intervals = {
        'CalotTriangleDissection': 8,
        'GallbladderDissection': 8,
        'CleaningCoagulation': 2,
        'ClippingCutting': 2,
        'Preparation': 1,
        'GallbladderPackaging': 1,
        'GallbladderRetraction': 1
    }
    return intervals.get(phase_name, 1)

def process_video(video_path, frames_dir, phase_info):
    # 确保输出目录存在
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_path}")
        return
        
    # 获取视频的FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    frame_count = 0
    print(f"正在处理视频: {video_name}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        current_second = int(frame_count / fps)
        
        # 确定当前帧所属的阶段
        current_phase = None
        for phase_name, (start, end) in phase_info[video_name].items():
            if start <= frame_count <= end:
                current_phase = phase_name
                break
        
        if current_phase:
            interval = get_frame_interval(current_phase)
            # 每隔interval秒保存一帧
            if current_second % interval == 0:
                frame_path = os.path.join(frames_dir, f"{current_second:06d}.jpg")
                cv2.imwrite(frame_path, frame)
            
        frame_count += 1
        
    print(f"视频 {video_name} 处理完成")
    cap.release()

def extract_frames(video_dir, output_dir, count_file, max_workers=4):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取阶段信息
    phase_info = read_phase_info(count_file)
    
    # 创建线程池
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for video_name in os.listdir(video_dir):
            if not video_name.endswith('.mp4'):
                continue
                
            video_path = os.path.join(video_dir, video_name)
            video_name_without_ext = os.path.splitext(video_name)[0]
            frames_dir = os.path.join(output_dir, video_name_without_ext)
            
            # 提交任务到线程池
            future = executor.submit(
                process_video,
                video_path,
                frames_dir,
                phase_info
            )
            futures.append(future)
        
        # 等待所有任务完成
        for future in futures:
            future.result()

if __name__ == "__main__":
    video_dir = "/mnt/data/cholec80/videos"
    output_dir = "/mnt/data/cholec80/frames_balance"
    count_file = "/mnt/data/cholec80/count.txt"
    extract_frames(video_dir, output_dir, count_file, max_workers=48)  # 32核CPU设置48个线程 