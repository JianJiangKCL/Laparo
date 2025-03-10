import os
import json

# Phase mapping
phase_mapping = {
    1: "Preparation",
    2: "Dividing Ligament and Peritoneum",
    3: "Dividing Uterine Vessels and Ligament",
    4: "Transecting the Vagina",
    5: "Specimen Removal",
    6: "Suturing",
    7: "Washing"
}

# Directory containing the label files
labels_dir = "/opt/liblibai-models/user-workspace/jj/datasets/autolaparo/labels"
output_file = "merged_labels.jsonl"

with open(output_file, 'w', encoding='utf-8') as outfile:
    # Process each label file
    for filename in sorted(os.listdir(labels_dir)):
        if not filename.startswith('label_') or not filename.endswith('.txt'):
            continue
            
        video_id = filename[6:8]  # Extract video ID (e.g., "01" from "label_01.txt")
        
        with open(os.path.join(labels_dir, filename), 'r') as f:
            # Skip header line
            next(f)
            
            # Process each line
            for line in f:
                frame_id, phase = line.strip().split('\t')
                phase = int(phase)
                
                # Create entry
                entry = {
                    "image_path": f"/opt/liblibai-models/user-workspace/jj/datasets/autolaparo/frames_1fps/{video_id}/{frame_id}.jpg",
                    "dataset": "autolaparo",
                    "phase": phase_mapping[phase],
                    "id": f"{video_id}{frame_id}"
                }
                
                # Write to JSONL file
                json.dump(entry, outfile, ensure_ascii=False)
                outfile.write('\n')

print(f"Conversion complete. Output saved to {output_file}") 