# Cholect50 Data Preprocessing

This directory contains the scripts and configuration for preprocessing the Cholect50 dataset.

## Data Processing Workflow

1. **Data Organization**
   - Raw data is organized in video folders (VID01, VID02, etc.)
   - Each video folder contains frame images (000000.png, 000001.png, etc.)

2. **Data Processing Pipeline**
   ```
   Raw Videos/Images
         ↓
   Create JSONL files (task_ready/)
         ↓
   Split into train/val/test (ready/)
   ```

3. **Data Splitting**
   - The script `split_data.py` splits the data based on video IDs
   - Output files are prefixed with train/val/test
   - Files are saved in the `ready/` directory

## Dataset Split Details

The dataset is split into three sets based on video IDs:

### Training Set (35 videos)
```python
train_videos = [
    1, 15, 26, 40, 52, 65, 79,  # Group 1
    2, 18, 27, 43, 56, 66, 92,  # Group 2
    4, 22, 31, 47, 57, 68, 96,  # Group 3
    5, 23, 35, 48, 60, 70, 103, # Group 4
    13, 25, 36, 49, 62, 75, 110 # Group 5
]
```

### Validation Set (5 videos)
```python
val_videos = [8, 12, 29, 50, 78]
```

### Test Set (10 videos)
```python
test_videos = [6, 51, 10, 73, 14, 74, 32, 80, 42, 111]
```

## File Structure

```
Cholect50/
├── datasets/
│   └── ori_c50_loader.py  # Original dataset loader with split configuration
├── split_data.py          # Script for splitting JSONL files
└── README.md             # This file
```

## Data Types

The dataset includes several types of data:

1. **MCQ (Multiple Choice Questions)**
   - Tissue recognition
   - Action recognition
   - Tool recognition

2. **VQA (Visual Question Answering)**
   - Tissue questions
   - Action questions
   - Tool questions
   - Triplet questions (tool-action-target combinations)

## Usage

1. First, ensure all JSONL files are in the `task_ready/` directory
2. Run the splitting script:
   ```bash
   python split_data.py
   ```
3. Check the `ready/` directory for the split files:
   - `train_*.jsonl`
   - `val_*.jsonl`
   - `test_*.jsonl`

## Split Rationale

- Training set (70%): Covers diverse surgical scenarios and techniques
- Validation set (10%): Used for model tuning and early stopping
- Test set (20%): Reserved for final evaluation

The splits are designed to maintain a balanced distribution of surgical procedures and ensure that similar procedures are not split across sets.