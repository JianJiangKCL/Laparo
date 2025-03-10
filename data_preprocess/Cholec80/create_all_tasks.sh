#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p /opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80/task_ready

# Array of modes and categories
modes=("mcq" "vqa")
categories=("phase" "tool")

# Loop through all combinations
for mode in "${modes[@]}"; do
    for category in "${categories[@]}"; do
        echo "Generating ${mode}_${category} data..."
        python /opt/liblibai-models/user-workspace/jj/proj/Laparo/data_preprocess/Cholec80/create_recognition_data.py --mode "$mode" --category "$category"
    done
done

echo "All data generation completed!" 