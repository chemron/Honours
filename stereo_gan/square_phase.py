import numpy as np
import os

dir_in = "../data_collection/DATA/np_phase_map/"
dir_out = "DATA/S_MAP/"
os.makedirs(dir_out) if not os.path.exists(dir_out) else None
upsample = True

filenames = np.sort(os.listdir(dir_in))
for filename in filenames:
    print(filename)
    path = dir_in + filename
    img = np.load(path)
    img = img[:, 90:270]
    if upsample:
        import cv2
        img = cv2.resize(img,
                         dsize=(1024, 1024),
                         interpolation=cv2.INTER_CUBIC)

    np.save(dir_out + filename, img)
