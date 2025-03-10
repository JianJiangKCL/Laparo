import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import argparse
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def process_folder(folder_info):
    folder_path, sample_rate = folder_info
    
    # Get folder name (e.g., "01", "02", etc.)
    folder_name = os.path.basename(folder_path)
    
    # Create output subfolder
    output_subfolder = os.path.join(output_dir, folder_name)
    os.makedirs(output_subfolder, exist_ok=True)
    
    try:
        # Get all frame files
        frame_files = sorted(glob.glob(os.path.join(folder_path, '*.jpg')))
        
        saved_frames = 0
        total_frames = len(frame_files)
        
        logging.info(f"Processing folder {folder_name} (Sample rate: {sample_rate})...")
        
        # Sample frames
        for i, frame_path in enumerate(frame_files):
            if i % sample_rate == 0:
                frame_name = os.path.basename(frame_path)
                output_path = os.path.join(output_subfolder, frame_name)
                shutil.copy2(frame_path, output_path)
                saved_frames += 1
        
        logging.info(f"Completed {folder_name}: Saved {saved_frames} frames out of {total_frames} total frames")
        return folder_name, True
        
    except Exception as e:
        logging.error(f"Error processing folder {folder_name}: {str(e)}")
        return folder_name, False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample frames from existing frame sequences')
    parser.add_argument('--sample_rate', type=int, default=25, help='Sample every N frames (default: 25)')
    args = parser.parse_args()

    # Calculate the output FPS
    output_fps = 25 // args.sample_rate

    # Define input and output directories
    input_dir = '/opt/liblibai-models/user-workspace/jj/datasets/cholec80/frames'
    output_dir = f'/opt/liblibai-models/user-workspace/jj/datasets/cholec80/frames_{output_fps}fps'

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get list of frame folders (01, 02, etc.)
    frame_folders = sorted(glob.glob(os.path.join(input_dir, '[0-9][0-9]')))

    # Create list of (folder_path, sample_rate) tuples
    folder_tasks = [(folder_path, args.sample_rate) for folder_path in frame_folders]

    # Number of concurrent threads
    max_workers = min(len(frame_folders), os.cpu_count() * 2)

    # Process folders concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all folder processing tasks
        future_to_folder = {executor.submit(process_folder, task): task for task in folder_tasks}
        
        # Process completed tasks
        successful = 0
        failed = 0
        
        for future in as_completed(future_to_folder):
            folder_name, success = future.result()
            if success:
                successful += 1
            else:
                failed += 1

    logging.info(f"Processing completed. Successfully processed: {successful}, Failed: {failed}") 