import json
import os
import random
from collections import defaultdict, Counter
from pathlib import Path
import shutil

def read_jsonl_generator(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            yield json.loads(line.strip())

def count_lines(file_path):
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for _ in f:
            count += 1
    return count

def reservoir_sample(file_path, k):
    """
    Perform reservoir sampling to randomly select k items from a stream.
    This is memory efficient as it never holds more than k items in memory.
    """
    reservoir = []
    for i, item in enumerate(read_jsonl_generator(file_path)):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randrange(i + 1)
            if j < k:
                reservoir[j] = item
    return reservoir

def get_split_type(filename):
    """Get the split type (train/val/test) from filename."""
    if filename.startswith('train'):
        return 'train'
    elif filename.startswith('val'):
        return 'val'
    elif filename.startswith('test'):
        return 'test'
    else:
        raise ValueError(f"Unknown split type in filename: {filename}")

def merge_datasets():
    # Define dataset paths
    base_path = Path('data_json')
    output_dir = Path('merged_data')
    
    # Create output directory if it doesn't exist
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # Statistics
    dataset_stats = defaultdict(lambda: {'files': set(), 'total_examples': 0, 'original_examples': 0})
    split_stats = defaultdict(lambda: {'total': 0, 'datasets': set(), 'file_types': set()})
    
    # Process each dataset in the data_json directory
    datasets = [d.name for d in base_path.iterdir() if d.is_dir()]
    
    # Process each dataset
    for dataset in datasets:
        ready_path = base_path / dataset / 'ready'
        if not ready_path.exists():
            print(f"Warning: {ready_path} does not exist")
            continue
            
        # Process each file in the ready directory
        for input_path in ready_path.glob('*.jsonl'):
            file_name = input_path.name
            print(f"Processing {dataset}/{file_name}")
            
            # Get split type (train/val/test)
            split = get_split_type(file_name)
            output_path = output_dir / f"{split}.jsonl"
            
            # Count total lines in input file
            total_lines = count_lines(input_path)
            
            # Determine if we need to sample
            is_mcq = 'mcq' in file_name.lower()
            sample_size = int(total_lines * 0.2) if is_mcq else total_lines
            
            # Update statistics
            dataset_stats[dataset]['files'].add(file_name)
            dataset_stats[dataset]['total_examples'] += sample_size
            dataset_stats[dataset]['original_examples'] += total_lines
            
            split_stats[split]['total'] += sample_size
            split_stats[split]['datasets'].add(dataset)
            file_type = 'mcq' if is_mcq else 'vqa'
            split_stats[split]['file_types'].add(file_type)
            
            # Append to output file
            write_mode = 'a' if output_path.exists() else 'w'
            with open(output_path, write_mode, encoding='utf-8') as out_f:
                if is_mcq:
                    # Use reservoir sampling for MCQ files
                    sampled_data = reservoir_sample(input_path, sample_size)
                    for item in sampled_data:
                        # Add metadata to track source
                        item['_source'] = {'dataset': dataset, 'file': file_name}
                        out_f.write(json.dumps(item, ensure_ascii=False) + '\n')
                else:
                    # For non-MCQ files, we can stream directly
                    for item in read_jsonl_generator(input_path):
                        # Add metadata to track source
                        item['_source'] = {'dataset': dataset, 'file': file_name}
                        out_f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # Print statistics
    print("\nDataset Statistics:")
    print("=" * 50)
    for dataset, stats in dataset_stats.items():
        print(f"\nDataset: {dataset}")
        print(f"Original examples: {stats['original_examples']}")
        print(f"After sampling: {stats['total_examples']}")
        print(f"Files processed: {len(stats['files'])}")
        print("Files:", ", ".join(sorted(stats['files'])))
    
    print("\nMerged Split Statistics:")
    print("=" * 50)
    for split, stats in split_stats.items():
        print(f"\nSplit: {split}")
        print(f"Total examples: {stats['total']}")
        print(f"Source datasets: {', '.join(sorted(stats['datasets']))}")
        print(f"File types: {', '.join(sorted(stats['file_types']))}")
    
    total_original = sum(stats['original_examples'] for stats in dataset_stats.values())
    total_after_sampling = sum(stats['total_examples'] for stats in dataset_stats.values())
    print(f"\nTotal original examples across all datasets: {total_original}")
    print(f"Total examples after sampling: {total_after_sampling}")
    print(f"Total datasets processed: {len(dataset_stats)}")
    
    print("\nOutput files:")
    for split in ['train', 'val', 'test']:
        file_path = output_dir / f"{split}.jsonl"
        if file_path.exists():
            print(f"{split}.jsonl: {count_lines(file_path)} examples")
    
    print("\nMerging complete!")

if __name__ == '__main__':
    random.seed(42)  # For reproducibility
    merge_datasets() 