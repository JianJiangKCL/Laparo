import os
import json
import glob
from collections import defaultdict

def load_jsonl_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def get_video_id(frame_data):
    """Extract video ID from the image path or id field"""
    if 'id' in frame_data:
        # ID format is VVFFFFFF where VV is video number
        return int(frame_data['id'][:2])
    else:
        # Extract from image path
        image_path = frame_data['images'][0]
        video_folder = os.path.basename(os.path.dirname(image_path))
        return int(video_folder)

def group_by_video(data_list):
    """Group data entries by video ID"""
    video_groups = defaultdict(list)
    for entry in data_list:
        video_id = get_video_id(entry)
        video_groups[video_id].append(entry)
    return video_groups

def write_jsonl(data_list, output_file):
    """Write data to JSONL file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in data_list:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')

def main():
    # Define directories
    input_dir = '/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80/task_ready'
    output_dir = '/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80/ready'
    
    # Define video ID ranges for splits
    train_range = range(1, 41)    # 1-40
    val_range = range(41, 61)     # 41-60
    test_range = range(61, 81)    # 61-80
    
    # Get all JSONL files in task_ready directory
    input_files = glob.glob(os.path.join(input_dir, '*.jsonl'))
    
    # Process each file
    for input_file in input_files:
        print(f"Processing {input_file}...")
        
        # Load data
        data_list = load_jsonl_data(input_file)
        
        # Group by video
        video_groups = group_by_video(data_list)
        
        # Split data based on video ID ranges
        train_data = [entry for vid in train_range for entry in video_groups.get(vid, [])]
        val_data = [entry for vid in val_range for entry in video_groups.get(vid, [])]
        test_data = [entry for vid in test_range for entry in video_groups.get(vid, [])]
        
        # Generate output filenames
        filename = os.path.basename(input_file)
        base_name = os.path.splitext(filename)[0]
        
        # Write split files
        write_jsonl(train_data, os.path.join(output_dir, f"train_{base_name}.jsonl"))
        write_jsonl(val_data, os.path.join(output_dir, f"val_{base_name}.jsonl"))
        write_jsonl(test_data, os.path.join(output_dir, f"test_{base_name}.jsonl"))
        
        # Count number of videos in each split
        train_videos = len(set(get_video_id(entry) for entry in train_data))
        val_videos = len(set(get_video_id(entry) for entry in val_data))
        test_videos = len(set(get_video_id(entry) for entry in test_data))
        
        print(f"Split sizes for {filename}:")
        print(f"  Train: {len(train_data)} samples from {train_videos} videos (videos 1-40)")
        print(f"  Val: {len(val_data)} samples from {val_videos} videos (videos 41-60)")
        print(f"  Test: {len(test_data)} samples from {test_videos} videos (videos 61-80)")
        print()

if __name__ == "__main__":
    main() 