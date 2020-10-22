# time python sort_data.py \
#     --input "../data_collection/DATA/png_aia/" \
#     --train "./DATA/aia_train/" \
#     --test "./DATA/aia_test/"

# time python sort_data.py \
#     --input "../data_collection/DATA/png_stereo/" \
#     --test "./DATA/stereo_test/"

time python sort_from_numpy_data.py \
    --input "AIA" \
    --func "_cube_root"