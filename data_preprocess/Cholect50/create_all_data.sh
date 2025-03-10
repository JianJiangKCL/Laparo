#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p data_json/Cholect50/ready

# Array of modes and categories
modes=("mcq" "vqa")
categories=("tissue" "action" "tool" "triplet")

# Loop through all combinations
for mode in "${modes[@]}"; do
    for category in "${categories[@]}"; do
        # Skip mcq_triplet as it's not supported
        if [ "$mode" = "mcq" ] && [ "$category" = "triplet" ]; then
            echo "Skipping mcq_triplet as it's not supported"
            continue
        fi
        
        echo "Generating ${mode}_${category} data..."
        python create_recognition_data.py --mode "$mode" --category "$category"
    done
done

echo "All data generation completed!" 