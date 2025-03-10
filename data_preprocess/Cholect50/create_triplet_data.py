import json
import os
import argparse
from datasets.ori_c50_loader import CholecT50
from torch.utils.data import DataLoader
from tqdm import tqdm

class CategoryMapper:
    def __init__(self,  json_path):
        with open(json_path, 'r') as f:
            categories = json.load(f)
        self.categories = categories

    def id2name(self, category_type, id):
        category = self.categories.get(category_type, {})
        return category.get(str(id), f"Unknown-{id}")

    def batch_id2name(self, category_type, ids):
        batch_categories = []
        # Handle binary matrix (BxD format)
        if ids.dim() > 1:
            # Iterate through each sample in the batch
            for sample in ids:
                # Get indices where value is 1 for this sample
                sample_indices = sample.nonzero().squeeze(1).tolist()
                # Convert indices to category names
                sample_categories = [self.id2name(category_type, idx) for idx in sample_indices]
                batch_categories.append(sample_categories)
        else:
            # Handle single sample case
            indices = ids.nonzero().squeeze(1).tolist()
            batch_categories = [self.id2name(category_type, idx) for idx in indices]
        
        return batch_categories

class JsonlGenerator:
    def __init__(self, dataset_dir, output_dir, category_mapping_path):
        self.dataset = CholecT50(
            dataset_dir=dataset_dir,
            dataset_variant="cholect50",
            test_fold=1,
            augmentation_list=['original']
        )
        self.output_dir = output_dir
        self.category_mapper = CategoryMapper(category_mapping_path)
        
    def generate_id_from_path(self, img_path):
        # Extract video number and frame number from path
        # Expected format: VIDxx/xxxxxx.png
        try:
            video_part = os.path.dirname(img_path).split('/')[-1]  # Get VIDxx
            frame_part = os.path.basename(img_path).split('.')[0]  # Get xxxxxx
            video_num = int(video_part[3:])  # Extract xx from VIDxx
            frame_num = int(frame_part)
            # Format: xxxnnnnnn where xxx is video number (3 digits) and nnnnnn is frame number
            return f"{video_num:03d}{frame_num:06d}"
        except:
            print(f"Warning: Could not parse ID from path {img_path}")
            return "000000000"
        
    def generate_jsonl_entry(self, img_path, label_ivt):
        triplet_names = self.category_mapper.batch_id2name("triplet", label_ivt)
        
        # Handle batch output by taking first item if it's a list of lists
        if isinstance(triplet_names[0], list):
            triplet_names = triplet_names[0]
        
        # Format each triplet with brackets
        formatted_triplets = []
        for triplet in triplet_names:
            parts = triplet.split(',')
            if len(parts) == 3:
                formatted_triplet = f"[{parts[0].strip()}]-[{parts[1].strip()}]-[{parts[2].strip()}]"
                formatted_triplets.append(formatted_triplet)
        
        # Create entry with ID based on video and frame numbers
        entry = {
            "image_path": img_path,
            "dataset": "cholect50",
            "triplets": formatted_triplets,
            "id": self.generate_id_from_path(img_path)
        }
        
        return entry
    
    def generate_all(self):
        train_dataset, val_dataset, test_dataset = self.dataset.build()
        
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, 'meta_triplet_data.jsonl')
        
        with open(output_file, 'w') as f:
            # Process training data
            train_loader = DataLoader(train_dataset, batch_size=1, shuffle=False)
            print("Processing training data...")
            for img_path, (label_ivt, _) in tqdm(train_loader):
                entry = self.generate_jsonl_entry(img_path[0], label_ivt)
                f.write(json.dumps(entry) + '\n')
                
            # Process validation data
            val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False)
            print("Processing validation data...")
            for img_path, (label_ivt, _) in tqdm(val_loader):
                entry = self.generate_jsonl_entry(img_path[0], label_ivt)
                f.write(json.dumps(entry) + '\n')
                
            # Process test data
            print("Processing test data...")
            for video_dataset in tqdm(test_dataset, desc="Processing videos"):
                test_loader = DataLoader(video_dataset, batch_size=1, shuffle=False)
                for img_path, (label_ivt, _) in test_loader:
                    entry = self.generate_jsonl_entry(img_path[0], label_ivt)
                    f.write(json.dumps(entry) + '\n')
        
        print(f"Generated entries in {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate JSONL file from CholecT50 dataset')
    parser.add_argument('--dataset_dir', type=str, 
                      default="/opt/liblibai-models/user-workspace/jj/datasets/ColecT50",
                      help='Directory containing the CholecT50 dataset')
    parser.add_argument('--output_dir', type=str, 
                      default="/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholect50",
                      help='Directory to save the output JSONL file')
    parser.add_argument('--category_mapping', type=str,
                      default="/opt/liblibai-models/user-workspace/jj/proj/Laparo/data_preprocess/Cholect50/datasets/category_mapping.json",
                      help='Path to the category mapping JSON file')
    
    args = parser.parse_args()
    
    generator = JsonlGenerator(
        dataset_dir=args.dataset_dir,
        output_dir=args.output_dir,
        category_mapping_path=args.category_mapping
    )
    generator.generate_all() 