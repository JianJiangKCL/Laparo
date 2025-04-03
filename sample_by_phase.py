import jsonlines
import random
import json
from pathlib import Path
import collections
import argparse
from typing import Dict, List, Any

def sample_by_phase(input_file: str, output_file: str, samples_per_phase: int = 1000) -> Dict[str, int]:
    """
    Sample a specific number of items from each phase in a JSONL file.
    
    Args:
        input_file: Path to the input JSONL file
        output_file: Path to the output JSONL file
        samples_per_phase: Number of samples to take from each phase (default: 1000)
        
    Returns:
        Dictionary with phase names as keys and number of samples taken as values
    """
    # Group data by phase
    phase_data: Dict[str, List[Any]] = collections.defaultdict(list)
    
    # Read all data from input file
    with jsonlines.open(input_file) as reader:
        for obj in reader:
            # Extract phase from meta field
            if "meta" in obj and "phase" in obj["meta"]:
                phase = obj["meta"]["phase"]
                phase_data[phase].append(obj)
            else:
                print(f"Warning: Skipping item with missing phase information")
    
    # Sample data from each phase
    sampled_data = []
    samples_count = {}
    
    for phase, items in phase_data.items():
        total_records = len(items)
        actual_sample_size = min(total_records, samples_per_phase)
        
        if total_records < samples_per_phase:
            print(f"Warning: Phase '{phase}' only has {total_records} records, which is less than requested {samples_per_phase}")
        
        phase_samples = random.sample(items, actual_sample_size)
        sampled_data.extend(phase_samples)
        samples_count[phase] = actual_sample_size
        
        print(f"Sampled {actual_sample_size} records from phase '{phase}' (out of {total_records} total)")
    
    # Write sampled data to output file
    with jsonlines.open(output_file, mode='w') as writer:
        writer.write_all(sampled_data)
    
    print(f"Total samples: {len(sampled_data)}")
    print(f"Output saved to: {output_file}")
    
    return samples_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample data from each phase in a JSONL file")
    parser.add_argument("--input", required=True, help="Path to the input JSONL file")
    parser.add_argument("--output", required=True, help="Path to the output JSONL file")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples per phase (default: 1000)")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Sample the data
    result = sample_by_phase(args.input, args.output, args.samples)
    
    # Print summary
    print("\nSampling summary:")
    for phase, count in result.items():
        print(f"  {phase}: {count} samples") 