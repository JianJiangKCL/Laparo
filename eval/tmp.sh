 CUDA_VISIBLE_DEVICES=0 swift infer --ckpt_dir /opt/liblibai-models/user-workspace/jj/output/v3-20250320-014533/checkpoint-39500 --attn_impl flash_attn --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/phase_data/Cholec80_vqa_phase.jsonl



CUDA_VISIBLE_DEVICES=1 swift export \
    --adapters '/opt/liblibai-models/user-workspace/jj/output/v3-20250320-014533/checkpoint-41200' \
    --merge_lora true


#16 爆内存； 4或者 2 会中途爆显存
MAX_PIXELS=1003520 \
CUDA_VISIBLE_DEVICES=0 \
   swift infer --ckpt_dir /opt/liblibai-models/user-workspace/jj/output/checkpoint-39500-merged --attn_impl flash_attn --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/NUS_test_data/phase_data/Cholec80_mcq_phase.jsonl --max_batch_size 1
   --infer_backend vllm --gpu_memory_utilization 0.9 

MAX_PIXELS=1003520 \
CUDA_VISIBLE_DEVICES=0 \
   swift infer --ckpt_dir /opt/liblibai-models/user-workspace/jj/output/checkpoint-41200-merged --attn_impl flash_attn --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/Cholec80/ready/test_vqa_phase.jsonl --max_batch_size 16   --infer_backend lmdeploy


MAX_PIXELS=1003520 \
CUDA_VISIBLE_DEVICES=1 \
   swift infer --ckpt_dir /opt/liblibai-models/user-workspace/jj/output/v3-20250320-014533/checkpoint-39500-merged --attn_impl flash_attn --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/NUS_test_data/phase_data/Cholec80_vqa_phase.jsonl --max_batch_size 16   --infer_backend lmdeploy


MAX_PIXELS=1003520 \
CUDA_VISIBLE_DEVICES=7 \
   swift infer --ckpt_dir /opt/liblibai-models/user-workspace/jj/output/checkpoint-39500-merged  --attn_impl flash_attn --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/data_json/autoLaparo/ready/test_phase.jsonl --max_batch_size 16   --infer_backend lmdeploy


CUDA_VISIBLE_DEVICES=0 swift infer \
    --ckpt_dir /opt/liblibai-models/user-workspace/jj/output/checkpoint-39500-merged \
    --attn_impl flash_attn \
    --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/phase_data/Cholec80_vqa_phase.jsonl \
    --result_path /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/full_results/Cholec80_vqa_phase_results.jsonl \
    --max_batch_size 16 \
    --infer_backend lmdeploy


python eval/evaluate_accuracy.py --input_file /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/full_results/Cholec80/ready/test_vqa_phase_results.jsonl   --output /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/full_results_acc/Cholec80_vqa_phase_acc.jsonl

python eval/evaluate_accuracy.py --input_file /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/full_results/Cholec80/ready/test_mcq_phase_results.jsonl   --output /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/full_results_acc/Cholec80_mcq_phase_acc.jsonl
