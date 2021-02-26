# python mag_vs_hmi.py \
#     --model_name 'P100_2' \
#     --input "AIA" \
#     --output "HMI"
time python mag_vs_hmi.py \
    --model_name 'P100_cube_root' \
    --input "AIA" \
    --output "HMI" \
    --func "_cube_root"
