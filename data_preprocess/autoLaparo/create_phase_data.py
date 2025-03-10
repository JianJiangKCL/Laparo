import json
import os
import sys

def convert_to_phase_format(input_file, output_file):
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

    count = 0
    try:
        with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
            for line in f_in:
                data = json.loads(line.strip())
                
                # Create the phase format
                phase_data = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a surgical expert."
                        },
                        {
                            "role": "user",
                            "content": "Given the hysterectomy surgical image <image>, answer what is the current phase?"
                        },
                        {
                            "role": "assistant",
                            "content": f"The current phase is {data['phase']}"
                        }
                    ],
                    "images": [data['image_path']]
                }
                
                # Write to output file
                json.dump(phase_data, f_out, ensure_ascii=False)
                f_out.write('\n')
                count += 1
        
        print(f"Successfully processed {count} entries")
        print(f"Output file created at: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"Error during file processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    input_file = "/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/merged_labels.jsonl"
    output_file = "/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/phase.jsonl"
    print(f"Current working directory: {os.getcwd()}")
    convert_to_phase_format(input_file, output_file) 