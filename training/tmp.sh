# eval_limit: 每个评测集的采样数，默认为None，表示使用全部数据，可用于快速验证

# eval_dataset: 评测数据集，可设置多个数据集，用空格分割

CUDA_VISIBLE_DEVICES=1,2,3,4,5,6,7 \
NPROC_PER_NODE=7 \
swift sft \
    --model /opt/liblibai-models/user-workspace/jj/ckpt/Qwen/Qwen2.5-VL-7B-Instruct \
    --train_type lora \
    --dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/train.jsonl \
    --val_dataset /opt/liblibai-models/user-workspace/jj/proj/Laparo/merged_data/val.jsonl \
    --eval_limit 1000 \
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
    --save_total_limit 50 \
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
    --padding_side left