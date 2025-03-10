import json
import os
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Split JSONL data into train/val/test sets')
    # parser.add_argument('--input_file', default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/mcq_phase.jsonl', type=str, help='Path to input JSONL file')
    parser.add_argument('--input_file', default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/phase.jsonl', type=str, help='Path to input JSONL file')
    parser.add_argument('--output_dir', type=str, 
                       default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/ready',
                       help='Output directory for split datasets')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Get input file and determine output paths
    input_file = args.input_file
    input_filename = os.path.basename(input_file)
    input_name = os.path.splitext(input_filename)[0]  # Remove .jsonl extension
    output_dir = args.output_dir

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize output files with input filename as prefix
    train_file = os.path.join(output_dir, f"train_{input_filename}")
    val_file = os.path.join(output_dir, f"val_{input_filename}")
    test_file = os.path.join(output_dir, f"test_{input_filename}")

    # Define video ID ranges for each split
    train_videos = set(f"{i:02d}" for i in range(1, 11))  # 01-10
    val_videos = set(f"{i:02d}" for i in range(11, 15))   # 11-14
    test_videos = set(f"{i:02d}" for i in range(15, 22))  # 15-21

    def get_video_id(image_path):
        # Extract video ID from image path like ".../frames_1fps/01/0001.jpg"
        parts = image_path.split('/')
        return parts[-2]  # Returns "01", "02", etc.

    # Process the input file and split into train/val/test
    with open(input_file, 'r') as f:
        # Open output files
        with open(train_file, 'w') as train_f, \
             open(val_file, 'w') as val_f, \
             open(test_file, 'w') as test_f:
            
            for line in f:
                if not line.strip():
                    continue
                    
                data = json.loads(line)
                video_id = get_video_id(data['images'][0])
                
                # Write to appropriate output file
                if video_id in train_videos:
                    train_f.write(line)
                elif video_id in val_videos:
                    val_f.write(line)
                elif video_id in test_videos:
                    test_f.write(line)

    print("Data splitting completed!")
    print(f"Files created in {output_dir}:")
    print(f"- train_{input_filename}")
    print(f"- val_{input_filename}")
    print(f"- test_{input_filename}")

if __name__ == "__main__":
    main() 