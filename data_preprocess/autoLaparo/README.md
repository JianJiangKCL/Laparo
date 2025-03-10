# AutoLaparo Data Preprocessing Workflow

This directory contains the preprocessing scripts for the AutoLaparo dataset, which focuses on surgical workflow recognition in laparoscopic hysterectomy procedures.

## Dataset Overview

The AutoLaparo dataset consists of:
- 21 laparoscopic hysterectomy videos (.mp4)
- Phase annotations at 1 fps (.txt)
- Multiple surgical phases documentation

### Surgical Phases
The procedure is divided into 7 distinct phases:
1. Preparation
2. Dividing Ligament and Peritoneum
3. Dividing Uterine Vessels and Ligament
4. Transecting the Vagina
5. Specimen Removal
6. Suturing
7. Washing

## Preprocessing Workflow

### 1. Video to Frame Extraction (`t1_video2frame.py`)
- Converts source videos to frames at 1 FPS
- Process:
  - Downsamples from 25 FPS to 1 FPS
  - Removes black borders from frames
  - Resizes images to 250x250 pixels
  - Organizes frames in numbered directories

### 2. Frame Extraction Script (`extract_1fps.sh`)
- Shell script for batch processing of video frame extraction
- Handles multiple video files sequentially

### 3. Phase Data Creation (`create_phase_data.py`)
- Processes phase annotations
- Creates structured phase data for model training

### 4. MCQ Data Formatting (`create_formate_MCQ_data.py`)
- Formats data for multiple-choice question tasks
- Prepares data for model training

### 5. Data Splitting (`split_data.py`)
- Splits the dataset into training, validation, and testing sets
- Default split:
  - Training: videos 01-10
  - Validation: videos 11-14
  - Testing: videos 15-21

## Usage

1. First, ensure your video data is placed in the correct directory structure
2. Run the preprocessing scripts in order:
   ```bash
   python t1_video2frame.py
   ./extract_1fps.sh
   python create_phase_data.py
   python create_formate_MCQ_data.py
   python split_data.py
   ```

## Citation

If you use this dataset or code in your research, please cite:

```bibtex
@article{wang2022autolaparo,
  title={AutoLaparo: A New Dataset of Integrated Multi-tasks for Image-guided Surgical Automation in Laparoscopic Hysterectomy},
  author={Wang, Ziyi and Lu, Bo and Long, Yonghao and Zhong, Fangxun and Cheung, Tak-Hong and Dou, Qi and Liu, Yunhui},
  journal={arXiv preprint arXiv:2208.02049},
  year={2022}
}
```

## License

- This dataset is for research purposes only
- Commercial use is not permitted
- Citation is required when using the dataset

## Resources

- Paper: [arXiv:2208.02049](https://arxiv.org/abs/2208.02049)
- Code: [GitHub Repository](https://github.com/ziyiwangx/AutoLaparo)
- Website: [AutoLaparo Project](https://autolaparo.github.io)

## Contact

For questions or issues, please contact: ziyiwangx@gmail.com 