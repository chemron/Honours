# python get_fits.py \
#         --STEREO \
#         --STEREO_path './DATA/fits_stereo' \
#         --STEREO_start '2010-04-26 00:00:00' \
#         --STEREO_end '2020-08-03 00:00:00' \
#         --wavelength 304

#         # --AIA \
#         # --HMI \
#         # --start '2011/01/01 00:00:00' \
#         # --end '2017/01/01 00:00:00' \
#         # --cadence 12 \
#         # --AIA_path './DATA/fits_aia' \
#         # --HMI_path './DATA/fits_hmi' \

# python get_data.py \
#         --instruments 'AIA' \
#         --series 'aia.lev1_euv_12s' \
#         --segment 'image' \
#         --start '2010-01-01 00:00:00' \
#         --end '2020-01-01 00:00:00' \
#         --cadence 12 \
#         --path  './DATA/' \
#         --wavelength 304 \

python get_data.py \
        --instruments 'HMI' \
        --series 'hmi.m_45s' \
        --segment 'magnetogram' \
        --start '2010-01-01 00:00:00' \
        --end '2020-01-01 00:00:00' \
        --cadence 12 \
        --path  './DATA/' \
        --wavelength 0 \
        --email "camerontasmith@gmail.com"

