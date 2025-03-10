import cv2
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def process_video(video_info):
    video_path, idx = video_info
    
    # Create subfolder name
    subfolder_name = f'{idx:02d}'
    subfolder_path = os.path.join(output_dir, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        logging.error(f"Error opening video file: {video_path}")
        return idx, False
    
    try:
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_number = 0
        
        logging.info(f"Processing video {subfolder_name} (FPS: {fps:.2f})...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Save every frame (at original FPS)
            frame_filename = f'{frame_number:05d}.jpg'
            frame_path = os.path.join(subfolder_path, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_number += 1
        
        logging.info(f"Completed {subfolder_name}: Saved {frame_number} frames")
        return idx, True
        
    except Exception as e:
        logging.error(f"Error processing video {subfolder_name}: {str(e)}")
        return idx, False
        
    finally:
        cap.release()

# Define input and output directories
input_dir = '/opt/liblibai-models/user-workspace/jj/datasets/cholec80/videos'
output_dir = '/opt/liblibai-models/user-workspace/jj/datasets/cholec80/frames'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get list of video files
video_files = sorted(glob.glob(os.path.join(input_dir, '*.mp4')))  # Assuming videos are in mp4 format

# Create list of (video_path, idx) tuples
video_tasks = [(video_path, idx) for idx, video_path in enumerate(video_files, 1)]

# Number of concurrent threads (adjust based on your system's capabilities)
max_workers = min(len(video_files), os.cpu_count() * 2)

# Process videos concurrently
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # Submit all video processing tasks
    future_to_video = {executor.submit(process_video, task): task for task in video_tasks}
    
    # Process completed tasks
    successful = 0
    failed = 0
    
    for future in as_completed(future_to_video):
        video_idx, success = future.result()
        if success:
            successful += 1
        else:
            failed += 1

logging.info(f"Processing completed. Successfully processed: {successful}, Failed: {failed}") 