import numpy as np
import os

dir_in = "DATA/np_phase_map/"
dir_out = "DATA/np_phase_map_square/"
os.makedirs(dir_out) if not os.path.exists(dir_out) else None

filenames = os.listdir(dir_in)[::365]
for filename in filenames:
    path = dir_in + filename
    img = np.load(path)
    img = img[:, 90:270]
    print(img.shape)
    np.save(dir_out + filename, img)
