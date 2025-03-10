import os
import glob
import json
import logging
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def read_tool_annotation(txt_path):
    """Read tool annotation file and return a dictionary mapping frame numbers to tool states"""
    tool_dict = {}
    tool_names = ['Grasper', 'Bipolar', 'Hook', 'Scissors', 'Clipper', 'Irrigator', 'SpecimenBag']
    
    with open(txt_path, 'r') as f:
        # Skip header line
        next(f)
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 8:  # Frame number + 7 tool states
                frame_num = int(parts[0])
                # Only include tools that are present (1/true)
                present_tools = [tool for tool, state in zip(tool_names, parts[1:8]) if int(state) == 1]
                tool_dict[frame_num] = present_tools
    return tool_dict

def read_phase_annotation(txt_path):
    """Read phase annotation file and return a dictionary mapping frame numbers to phases"""
    phase_dict = {}
    with open(txt_path, 'r') as f:
        # Skip header line
        next(f)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                frame_num = int(parts[0])
                phase = parts[1]
                phase_dict[frame_num] = phase
    return phase_dict

def process_video_folder(folder_path, phase_dict, tool_dict, frames_dir):
    """Process a single video folder and return metadata for all frames"""
    folder_name = os.path.basename(folder_path)
    video_id = int(folder_name)
    
    frame_files = sorted(glob.glob(os.path.join(folder_path, '*.jpg')))
    metadata_list = []
    
    for frame_path in frame_files:
        frame_name = os.path.basename(frame_path)
        frame_number = int(frame_name.split('.')[0])
        
        # Get phase for this frame number
        phase = phase_dict.get(frame_number, "Unknown")
        
        # Get tool states for this frame number
        tools = tool_dict.get(frame_number, [])
        
        # Create ID in format VVFFFFFF where VV is video number and FFFFFF is frame number (6 digits)
        id_str = f"{video_id:02d}{frame_number:06d}"
        
        # Create absolute path
        rel_path = os.path.join(folder_name, frame_name)
        abs_path = os.path.join(frames_dir, rel_path)
        
        metadata = {
            "image_path": abs_path,
            "dataset": "cholec80",
            "phase": phase,
            "tools": tools,
            "id": id_str
        }
        metadata_list.append(metadata)
    
    return metadata_list

def main():
    # Define directories
    frames_dir = '/opt/liblibai-models/user-workspace/jj/datasets/cholec80/frames_sample_rate_25'
    annotations_dir = '/opt/liblibai-models/user-workspace/jj/datasets/cholec80/phase_annotations'
    tool_annotations_dir = '/opt/liblibai-models/user-workspace/jj/datasets/cholec80/tool_annotations'
    output_dir = '/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output file path
    output_file = os.path.join(output_dir, 'meta_data.jsonl')
    
    # Get all video folders
    video_folders = sorted(glob.glob(os.path.join(frames_dir, '[0-9][0-9]')))
    
    # Process each video folder
    with open(output_file, 'w', encoding='utf-8') as f:
        for folder_path in video_folders:
            folder_name = os.path.basename(folder_path)
            video_id = int(folder_name)
            
            # Find corresponding annotation files
            phase_file = os.path.join(annotations_dir, f'video{video_id:02d}-phase.txt')
            tool_file = os.path.join(tool_annotations_dir, f'video{video_id:02d}-tool.txt')
            
            logging.info(f"Looking for annotation files:\nPhase: {phase_file}\nTools: {tool_file}")
            
            if not os.path.exists(phase_file) or not os.path.exists(tool_file):
                logging.warning(f"Annotation files not found for video {video_id:02d}")
                continue
                
            logging.info(f"Processing video {video_id:02d}...")
            
            try:
                # Read phase and tool annotations
                phase_dict = read_phase_annotation(phase_file)
                tool_dict = read_tool_annotation(tool_file)
                
                # Process frames and write metadata
                metadata_list = process_video_folder(folder_path, phase_dict, tool_dict, frames_dir)
                
                # Write to jsonl file
                for metadata in metadata_list:
                    f.write(json.dumps(metadata) + '\n')
                
                logging.info(f"Completed video {video_id:02d}: {len(metadata_list)} frames processed")
            except Exception as e:
                logging.error(f"Error processing video {video_id:02d}: {str(e)}")
                continue

if __name__ == "__main__":
    main()
    logging.info("Metadata creation completed") 