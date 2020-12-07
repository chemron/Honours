import os
import numpy as np
import cv2
from normalise_stereo_p import (rolling_75p, clip_max, outlier_indicies, dates,
                                zero_point, q)

w = h = 1024  # desired width and height of output
n = 50
func = ''
np_dir = "DATA/np_STEREO/"
normal_np_dir = f"DATA/np_STEREO_normalised{func}/"
os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None

data = np.sort(os.listdir(np_dir))
data = np.delete(data, outlier_indicies)
data = data[n//2-1:-n//2]
assert len(dates) == len(data)

# normal percentiles and corresponding dates
normal_p = []
normal_d = []

for i in range(len(data)):
    # what we need to divide by to normalise with clip_max at 1
    name = data[i]
    divider = rolling_75p[i] * clip_max
    filename = np_dir + name
    img = np.load(filename)
    img -= zero_point
    img = img/divider
    img = img.clip(0, 1)
    img = np.sign(img) * (np.abs(img) ** (1/2))
    try:
        img = cv2.resize(img, dsize=(w, h))
        np.save(normal_np_dir + name, img)
    except cv2.error as e:
        print(f"{name}: {e}")

    percentiles = np.percentile(data, q)
    if percentiles is not None:
        normal_p.append(percentiles)
        normal_d.append(dates[i])


percentile_dir = "DATA/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

np.save(f"{percentile_dir}STEREO_normal_p", percentiles)
np.save(f"{percentile_dir}STEREO_normal_d", dates)
