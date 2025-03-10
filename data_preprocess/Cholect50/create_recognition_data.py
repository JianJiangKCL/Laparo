import argparse
import json
import random
import os
import sys

def load_category_mapping(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def load_jsonl_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def get_category_from_triplets(triplets, category):
    """Extract all values for a given category from triplets."""
    values = []
    for triplet in triplets:
        parts = triplet.strip('[]').split(']-[')
        if category == "tool":
            values.append(parts[0])
        elif category == "action":
            values.append(parts[1])
        elif category == "tissue":
            values.append(parts[2])
    return values

def create_mcq_question(category, mapping, frame_data):
    # Skip if category is triplet
    if category == "triplet":
        return None
        
    # Get triplets from frame data
    triplets = frame_data.get("triplets", [])
    # Skip if there are no triplets or more than one triplet
    if not triplets or len(triplets) > 1:
        return None
    
    # Get all values for the category from triplets
    category_values = get_category_from_triplets(triplets, category)
    
    # Remove null values
    valid_values = [v for v in category_values if not v.startswith("null_")]
    if not valid_values:
        return None
    
    # Select a random non-null value as correct answer
    correct_answer = random.choice(valid_values)
    
    # Set up question and options based on category
    if category == "tissue":
        options = list(mapping["target"].values())
        question = "Given the cholecystectomy surgical image <image>, which organ/tissue is being operated?"
    elif category == "action":
        options = list(mapping["verb"].values())
        question = "Given the cholecystectomy surgical image <image>, what action is being performed?"
    elif category == "tool":
        options = list(mapping["instrument"].values())
        question = "Given the cholecystectomy surgical image <image>, what surgical instrument is being used?"
    else:
        raise ValueError(f"Invalid category: {category}")
    
    # Remove null options
    options = [opt for opt in options if not opt.startswith("null")]
    
    # Get distractors (excluding the correct answer)
    other_options = [opt for opt in options if opt != correct_answer]
    distractors = random.sample(other_options, min(4, len(other_options)))
    
    # Ensure we have exactly 5 options (ABCDE)
    while len(distractors) < 4:
        distractors.append(f"None of the above")
    
    all_options = [correct_answer] + distractors
    random.shuffle(all_options)
    
    # Create option mapping and option strings
    option_mapping = {chr(65+i): opt for i, opt in enumerate(all_options)}
    option_strings = [f"{k}. {v}" for k, v in option_mapping.items()]
    correct_option = [k for k, v in option_mapping.items() if v == correct_answer][0]
    
    # Create formatted data
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
        "images": [frame_data.get("image_path", "")]
    }
    
    return formatted_data

def create_vqa_question(category, frame_data):
    # Get triplets from frame data
    triplets = frame_data.get("triplets", [])
    if not triplets:
        return None
    
    if category == "triplet":
        # For triplet, we'll ask about the complete action
        # Select a random triplet as answer
        answer = random.choice(triplets)
        question = "Given the cholecystectomy surgical image <image>, describe the complete surgical action in terms of tool, action, and tissue."
        # Format the triplet nicely by removing brackets and replacing ]-[ with spaces
        formatted_answer = answer.strip('[]').replace("]-[", " ")
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
                    "content": f"The complete surgical action is: {formatted_answer}"
                }
            ],
            "images": [frame_data.get("image_path", "")]
        }
        return formatted_data
    
    # Get all values for the category from triplets
    category_values = get_category_from_triplets(triplets, category)
    
    # Remove null values
    valid_values = [v for v in category_values if not v.startswith("null_")]
    if not valid_values:
        return None
    
    # For VQA, use all unique non-null values as the answer
    unique_answers = list(set(valid_values))
    
    # Set up question based on category
    if category == "tissue":
        question = "Given the cholecystectomy surgical image <image>, what organ or tissue is being operated on?"
    elif category == "action":
        question = "Given the cholecystectomy surgical image <image>, what surgical action is being performed?"
    elif category == "tool":
        question = "Given the cholecystectomy surgical image <image>, what surgical instrument is being used?"
    else:
        raise ValueError(f"Invalid category: {category}")
    
    # Format multiple answers with commas and 'and'
    if len(unique_answers) == 1:
        answer_text = unique_answers[0]
    else:
        answer_text = ", ".join(unique_answers[:-1]) + " and " + unique_answers[-1]
    
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
                "content": f"The {category}{'s' if len(unique_answers) > 1 else ''} {'are' if len(unique_answers) > 1 else 'is'} {answer_text}"
            }
        ],
        "images": [frame_data.get("image_path", "")]
    }
    
    return formatted_data

def main():
    parser = argparse.ArgumentParser(description='Create recognition data for surgical video frames')
    parser.add_argument('--mode', choices=['mcq', 'vqa'], required=True, help='Mode of question generation')
    parser.add_argument('--category', choices=['tissue', 'action', 'tool', 'triplet'], required=True, help='Category of question')
    parser.add_argument('--mapping_file', type=str, 
                       default='data_preprocess/Cholect50/datasets/category_mapping.json',
                       help='Path to category mapping JSON file')
    parser.add_argument('--input_jsonl', type=str,
                       default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholect50/meta_triplet_data.jsonl',
                       help='Path to input JSONL file containing frame data')
    parser.add_argument('--output_dir', type=str,
                       default='/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholect50/ready',
                       help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate output filename
    output_file = os.path.join(args.output_dir, f"{args.mode}_{args.category}.jsonl")
    
    # Load category mapping and input data
    category_mapping = load_category_mapping(args.mapping_file)
    frame_data_list = load_jsonl_data(args.input_jsonl)
    
    # Process and write questions
    count = 0
    skipped = 0
    try:
        with open(output_file, 'w') as f_out:
            for frame_data in frame_data_list:
                if args.mode == 'mcq':
                    formatted_data = create_mcq_question(args.category, category_mapping, frame_data)
                else:  # vqa mode
                    formatted_data = create_vqa_question(args.category, frame_data)
                
                # Skip if formatted_data is None (null value case)
                if formatted_data is None:
                    skipped += 1
                    continue
                
                json.dump(formatted_data, f_out, ensure_ascii=False)
                f_out.write('\n')
                count += 1
        
        print(f"Successfully processed {count} entries")
        print(f"Skipped {skipped} entries with null values")
        print(f"Output file created at: {os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"Error during file processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 