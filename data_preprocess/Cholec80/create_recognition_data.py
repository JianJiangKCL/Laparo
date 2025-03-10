import argparse
import json
import random
import os
import sys

def load_jsonl_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def get_all_phases_and_tools(data_list):
    """Extract all unique phases and tools from the dataset."""
    phases = set()
    tools = set()
    for data in data_list:
        phases.add(data['phase'])
        tools.update(data['tools'])
    return list(phases - {'Unknown'}), list(tools)

def create_mcq_question(category, all_options, frame_data):
    if category == "phase":
        correct_answer = frame_data['phase']
        if correct_answer == "Unknown":
            return None
        question = "Given the cholecystectomy surgical image <image>, which surgical phase is being performed?"
    else:  # tool category
        tools = frame_data['tools']
        if not tools:  # Skip if no tools are present
            return None
        correct_answer = random.choice(tools)
        question = "Given the cholecystectomy surgical image <image>, which surgical instrument is being used?"
    
    # Get distractors (excluding the correct answer)
    other_options = [opt for opt in all_options if opt != correct_answer]
    distractors = random.sample(other_options, min(4, len(other_options)))
    
    # Ensure we have exactly 5 options (ABCDE)
    while len(distractors) < 4:
        distractors.append("None of the above")
    
    all_choices = [correct_answer] + distractors
    random.shuffle(all_choices)
    
    # Create option mapping and option strings
    option_mapping = {chr(65+i): opt for i, opt in enumerate(all_choices)}
    option_strings = [f"{k}. {v}" for k, v in option_mapping.items()]
    correct_option = [k for k, v in option_mapping.items() if v == correct_answer][0]
    
    formatted_data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a surgical expert."
            },
            {
                "role": "user",
                "content": question + "\n" + "\n".join(option_strings)
            },
            {
                "role": "assistant",
                "content": f"{correct_option}. {correct_answer}"
            }
        ],
        "images": [frame_data["image_path"]]
    }
    
    return formatted_data

def create_vqa_question(category, frame_data):
    if category == "phase":
        phase = frame_data['phase']
        if phase == "Unknown":
            return None
        question = "Given the cholecystectomy surgical image <image>, which surgical phase is being performed?"
        answer_text = phase
    else:  # tool category
        tools = frame_data['tools']
        if not tools:  # Skip if no tools are present
            return None
        question = "Given the cholecystectomy surgical image <image>, what surgical instruments are being used?"
        # Format multiple tools with commas and 'and'
        if len(tools) == 1:
            answer_text = tools[0]
        else:
            answer_text = ", ".join(tools[:-1]) + " and " + tools[-1]
    
    formatted_data = {
        "messages": [
            {
                "role": "system",
                "content": "You are a surgical expert."
            },
            {
                "role": "user",
                "content": question
            },
            {
                "role": "assistant",
                "content": f"The {category}{'s' if category == 'tool' and len(tools) > 1 else ''} {'are' if category == 'tool' and len(tools) > 1 else 'is'} {answer_text}"
            }
        ],
        "images": [frame_data["image_path"]]
    }
    
    return formatted_data

def main():
    parser = argparse.ArgumentParser(description='Create recognition data for Cholec80 surgical video frames')
    parser.add_argument('--mode', choices=['mcq', 'vqa'], required=True, help='Mode of question generation')
    parser.add_argument('--category', choices=['phase', 'tool'], required=True, help='Category of question')
    parser.add_argument('--input_jsonl', type=str,
                       default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80/meta_data.jsonl',
                       help='Path to input JSONL file containing frame data')
    parser.add_argument('--output_dir', type=str,
                       default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80/task_ready',
                       help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate output filename
    output_file = os.path.join(args.output_dir, f"{args.mode}_{args.category}.jsonl")
    
    # Load input data
    frame_data_list = load_jsonl_data(args.input_jsonl)
    
    # Get all unique phases and tools
    all_phases, all_tools = get_all_phases_and_tools(frame_data_list)
    
    # Process and write questions
    count = 0
    skipped = 0
    try:
        with open(output_file, 'w') as f_out:
            for frame_data in frame_data_list:
                if args.mode == 'mcq':
                    formatted_data = create_mcq_question(
                        args.category,
                        all_phases if args.category == 'phase' else all_tools,
                        frame_data
                    )
                else:  # vqa mode
                    formatted_data = create_vqa_question(args.category, frame_data)
                
                # Skip if formatted_data is None
                if formatted_data is None:
                    skipped += 1
                    continue
                
                json.dump(formatted_data, f_out, ensure_ascii=False)
                f_out.write('\n')
                count += 1
        
        print(f"Successfully processed {count} entries")
        print(f"Skipped {skipped} entries")
        print(f"Output file created at: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"Error during file processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 