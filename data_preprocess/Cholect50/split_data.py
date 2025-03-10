import json
import os
from pathlib import Path

# Define the splits based on video IDs
VIDEO_SPLITS = {
    'train': [1, 15, 26, 40, 52, 65, 79, 2, 18, 27, 43, 56, 66, 92, 4, 22, 31, 47, 57, 68, 96, 5, 23, 35, 48, 60, 70, 103, 13, 25, 36, 49, 62, 75, 110],
    'val': [8, 12, 29, 50, 78],
    'test': [6, 51, 10, 73, 14, 74, 32, 80, 42, 111]
}

def get_video_id_from_path(path):
    # Extract video ID from path like "/opt/.../VID01/000000.png"
    # Split the path and find the component starting with "VID"
    parts = path.split('/')
    for part in parts:
        if part.startswith('VID'):
            return int(part[3:])  # Extract the number after "VID"
    return None

def process_jsonl_file(input_file, output_dir):
    # Get the base name without .jsonl extension
    base_name = os.path.basename(input_file)[:-6]
    
    # Create split files with split type as prefix
    output_files = {
        split: open(os.path.join(output_dir, f"{split}_{base_name}.jsonl"), 'w', encoding='utf-8')
        for split in VIDEO_SPLITS.keys()
    }
    
    # Process each line and write to appropriate split file
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            # Get the image path from the images list
            if 'images' in data and len(data['images']) > 0:
                image_path = data['images'][0]
                video_id = get_video_id_from_path(image_path)
                
                # Determine which split this example belongs to
                target_split = None
                for split, video_ids in VIDEO_SPLITS.items():
                    if video_id in video_ids:
                        target_split = split
                        break
                
                if target_split:
                    output_files[target_split].write(line)
    
    # Close all output files
    for f in output_files.values():
        f.close()

def main():
    input_dir = "/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholect50/task_ready"
    output_dir = "/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholect50/ready"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each JSONL file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.jsonl'):
            print(f"Processing {filename}...")
            input_file = os.path.join(input_dir, filename)
            process_jsonl_file(input_file, output_dir)
            print(f"Finished processing {filename}")

if __name__ == "__main__":
    main() 