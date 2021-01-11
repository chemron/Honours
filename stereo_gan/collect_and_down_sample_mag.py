import numpy as np
import os
import cv2

model = "P100_4"
dir_in = f"../kim_gan/RESULTS/{model}/STEREO_to_MAG/"
img_dir = np.sort(os.listdir(dir_in))[-1]
dir_in = dir_in + img_dir

dir_out = "DATA/MAG/"
os.makedirs(dir_out) if not os.path.exists(dir_out) else None

filenames = np.sort(os.listdir(dir_in))[::730]
for filename in filenames:
    print(filename)
    path = dir_in + filename
    img = np.load(path)
    img = cv2.resize(img, dsize=(180, 180), interpolation=cv2.INTER_CUBIC)
    np.save(dir_out + filename, img)
