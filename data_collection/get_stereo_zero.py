import numpy as np
import os

data_dir = "DATA/np_STEREO/"
data = np.sort(os.listdir(data_dir))

# percentiles of 0 in AIA data (what percentile zero occurs at)
AIA_zero_ps = np.load("DATA/np_objects/AIA_minp.npy")
# average zero:
av_AIA_zero_p = np.average(AIA_zero_ps)
stereo_zeros = []

# get equivalent zero:
for i in range(len(data)):
    name = data[i]
    print(name)
    filename = data_dir + name
    img = np.load(filename).flatten()
    stereo_zero = np.percentile(img, av_AIA_zero_p)
    stereo_zeros.append(stereo_zero)

np.save("DATA/np_objects/STEREO_zeros", np.array(stereo_zeros))
print(np.average(stereo_zeros))
