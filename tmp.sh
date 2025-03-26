# eval_limit: 每个评测集的采样数，默认为None，表示使用全部数据，可用于快速验证

# eval_dataset: 评测数据集，可设置多个数据集，用空格分割
CUDA_VISIBLE_DEVICES=0 \

CUDA_VISIBLE_DEVICES=1,2,3,4,5,6,7 \
NPROC_PER_NODE=7 \
swift sft \
    --model /opt/liblibai-models/user-workspace/jj/ckpt/Qwen/Qwen2.5-VL-7B-Instruct \
    --train_type lora \
    --dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/train.jsonl \
    --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/2000_val.jsonl \
    --torch_dtype bfloat16 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --output_dir output/ \
    --logging_dir output/ \
    --freeze_vit false \
    --lora_rank 32 \
    --lora_alpha 64 \
    --target_modules all-linear \
    --gradient_checkpointing false \
    --gradient_accumulation_steps 4 \
    --save_strategy "steps" \
    --save_steps 100 \
    --save_total_limit 10 \
    --num_train_epochs  3 \
    --learning_rate 5e-5 \
    --save_only_model false \
    --weight_decay 0.05 \
    --adam_beta2 0.95 \
    --lr_scheduler_type "cosine" \
    --logging_steps 100 \
    --eval_strategy "steps" \
    --eval_steps 500 \
    --warmup_ratio 0.05 \
    --dataset_num_proc 12 \
    --dataloader_num_workers 4 \
    --dataloader_pin_memory true \
    --ddp_backend "nccl" \
    --report_to wandb \
    --deepspeed zero3 \
    --max_length 4096 \
    --max_new_tokens 1024 \
    --attn_impl flash_attn  \
    --padding_side left \
    --resume_from_checkpoint /opt/liblibai-models/user-workspace/jj/output/v2-20250315-165430/checkpoint-38800
#糟糕，有max_length的限制，导致无法使用更大的模型


CUDA_VISIBLE_DEVICES=0 \
swift sft \
    --model /opt/liblibai-models/user-workspace/jj/ckpt/Qwen/Qwen2.5-VL-7B-Instruct \
    --train_type lora \
    --dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/train.jsonl \
    --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/2000_val.jsonl \
    --torch_dtype bfloat16 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --output_dir output/ \
    --logging_dir output/ \
    --freeze_vit false \
    --lora_rank 8 \
    --lora_alpha 16 \
    --target_modules all-linear \
    --gradient_checkpointing false \
    --gradient_accumulation_steps 4 \
    --save_strategy "steps" \
    --save_steps 100 \
    --save_total_limit 10 \
    --num_train_epochs  3 \
    --learning_rate 5e-5 \
    --save_only_model false \
    --weight_decay 0.05 \
    --adam_beta2 0.95 \
    --lr_scheduler_type "cosine" \
    --logging_steps 100 \
    --eval_strategy "steps" \
    --eval_steps 500 \
    --warmup_ratio 0.05 \
    --dataset_num_proc 12 \
    --dataloader_num_workers 4 \
    --dataloader_pin_memory true \
    --report_to wandb \
    --attn_impl flash_attn  \
    --padding_side left \
    --resume_from_checkpoint /opt/liblibai-models/user-workspace/jj/output/v1-20250314-215219/checkpoint-16900 \
    --deepspeed zero3 \
    --max_length 4096 \
    --max_new_tokens 1024 \

CUDA_VISIBLE_DEVICES=2 swift export \
    --adapters '/opt/liblibai-models/user-workspace/jj/proj/Laparo/grpo_output/v5-20250326-034249/checkpoint-800' \
    --merge_lora true
   

CUDA_VISIBLE_DEVICES=0 swift infer \
--ckpt_dir /opt/liblibai-models/user-workspace/jj/proj/Laparo/grpo_output/v5-checkpoint-400-merged \
--attn_impl flash_attn \
--val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/200_val_grpo.jsonl \
--infer_backend vllm \
--gpu_memory_utilization 0.7 \
--max_batch_size 8 \
--max_model_len 4096

CUDA_VISIBLE_DEVICES=0 swift infer \
--ckpt_dir /opt/liblibai-models/user-workspace/jj/output/checkpoint-39500-merged \
--attn_impl flash_attn \
--infer_backend vllm \
--gpu_memory_utilization 0.7 \
--val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/test_vqa_phase1500.jsonl \
--result_path /opt/liblibai-models/user-workspace/jj/proj/Laparo/eval/tmp/test_vqa_phase1500_results.jsonl

##############
# GRPO
CUDA_VISIBLE_DEVICES=0,2,3,4,5,6,7 \
NPROC_PER_NODE=6 \
swift rlhf \
    --rlhf_type grpo \
    --model /opt/liblibai-models/user-workspace/jj/output/checkpoint-39500-merged \
    --reward_funcs accuracy format \
    --train_type lora \
    --lora_rank 8 \
    --lora_alpha 32 \
    --target_modules all-linear \
    --torch_dtype bfloat16 \
    --dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/val_grpo.jsonl  \
    --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/200_val_grpo.jsonl  \
    --max_completion_length 1024 \
    --num_train_epochs 1 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --learning_rate 1e-5 \
    --gradient_accumulation_steps 4 \
    --eval_steps 500 \
    --save_steps 100 \
    --save_total_limit 10 \
    --logging_steps 100 \
    --output_dir grpo_output \
    --warmup_ratio 0.05 \
    --dataloader_num_workers 4 \
    --dataset_num_proc 4 \
    --num_generations 6 \
    --temperature 0.9 \
    --system /opt/liblibai-models/user-workspace/jj/proj/Laparo/grpo/prompt.txt \
    --deepspeed zero2 \
    --attn_impl flash_attn  \
    --padding_side left \
    --use_vllm true \
    --vllm_device auto \
    --vllm_gpu_memory_utilization 0.7 \
    --report_to wandb \
    --resume_from_checkpoint /opt/liblibai-models/user-workspace/jj/proj/Laparo/grpo_output/v5-20250326-034249/checkpoint-800 \
    --log_completions true


CUDA_VISIBLE_DEVICES=3 swift infer \
--ckpt_dir /opt/liblibai-models/user-workspace/jj/proj/Laparo/grpo_output/v5-checkpoint-800-merged \
--attn_impl flash_attn \
--val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/20_val_grpo.jsonl 


CUDA_VISIBLE_DEVICES=3 swift infer \
--ckpt_dir /opt/liblibai-models/user-workspace/jj/output/checkpoint-39500-merged \
--attn_impl flash_attn \
--val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/20_val_grpo.jsonl 
# \
# --infer_backend vllm \
# --gpu_memory_utilization 0.7 \



# --max_batch_size 6