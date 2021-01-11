import numpy as np
import os

dir_in = "DATA/np_phase_map/"
dir_out = "DATA/np_phase_map_square/"
os.makedirs(dir_out) if not os.path.exists(dir_out) else None

filenames = np.sort(os.listdir(dir_in))
for filename in filenames:
    print(filename)
    path = dir_in + filename
    img = np.load(path)
    img = img[:, 90:270]
    np.save(dir_out + filename, img)
