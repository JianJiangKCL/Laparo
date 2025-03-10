import json
import os
import sys
import random

def convert_to_mcq_format(input_file, output_file):
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist!")
        sys.exit(1)

    # Create output directory if it doesn't exist
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        print(f"Created/verified output directory: {os.path.dirname(output_file)}")
    except Exception as e:
        print(f"Error creating output directory: {e}")
        sys.exit(1)

    # Define all possible surgical phases
    all_phases = [
        "Preparation",
        "Dividing Ligament and Peritoneum",
        "Dividing Uterine Vessels and Ligament",
        "Transecting the Vagina",
        "Specimen Removal",
        "Suturing",
        "Washing"
    ]

    count = 0
    try:
        with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
            for line in f_in:
                data = json.loads(line.strip())
                correct_phase = data['phase']
                
                # Get other phases (excluding the correct one)
                other_phases = [p for p in all_phases if p != correct_phase]
                # Randomly select 4 distractors
                distractors = random.sample(other_phases, min(4, len(other_phases)))
                
                # Combine correct answer and distractors
                selected_phases = [correct_phase] + distractors
                # Shuffle the options
                random.shuffle(selected_phases)
                
                # Create option mapping and strings
                option_mapping = {chr(65+i): phase for i, phase in enumerate(selected_phases)}
                option_strings = [f"{k}. {v}" for k, v in option_mapping.items()]
                
                # Find the correct option letter
                correct_option = [k for k, v in option_mapping.items() if v == correct_phase][0]
                
                # Create the MCQ format
                mcq_data = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a surgical expert."
                        },
                        {
                            "role": "user",
                            "content": "Given the hysterectomy surgical image <image>, select the current surgical phase from the following options:\n" + "\n".join(option_strings)
                        },
                        {
                            "role": "assistant",
                            "content": f"{correct_option}. {correct_phase}"
                        }
                    ],
                    "images": [data['image_path']]
                }
                
                # Write to output file
                json.dump(mcq_data, f_out, ensure_ascii=False)
                f_out.write('\n')
                count += 1
        
        print(f"Successfully processed {count} entries")
        print(f"Output file created at: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"Error during file processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    input_file = "/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/meta_labels.jsonl"  # Added ./ to make path explicit
    output_file = "/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/mcq_phase.jsonl"  # Added ./ to make path explicit
    print(f"Current working directory: {os.getcwd()}")
    convert_to_mcq_format(input_file, output_file)