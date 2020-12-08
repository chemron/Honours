import os
from datetime import datetime
import numpy as np
from normalise_AIA_p import (rolling_75p, clip_max, outlier_indicies, q)

w = h = 1024  # desired width and height of output
n = 50
func = ''
mode = 'AIA'
np_dir = f"DATA/np_{mode}/"
normal_np_dir = f"DATA/np_{mode}_normalised{func}/"
os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None

data = np.sort(os.listdir(np_dir))
data = np.delete(data, outlier_indicies)
data = data[n//2:-n//2]

assert len(rolling_75p) == len(data)

# normal percentiles and corresponding dates
normal_p = []
normal_d = []


for i in range(len(data)):
    import cv2

    # what we need to divide by to normalise with clip_max at 1
    name = data[i]
    date_str = name.split('_')
    date_str = date_str[1] + date_str[2]
    date = datetime.strptime(date_str, '%Y.%m.%d%H:%M:%S')
    save_name = f'AIA_{date.year}.{date.month:0>2}.{date.day:0>2}_' \
                f'{date.hour:0>2}:{date.minute:0>2}:{date.second:0>2}'
    divider = rolling_75p[i] * clip_max
    filename = np_dir + name
    img = np.load(filename)
    img = img/divider
    img = img.clip(0, 1)
    img = np.sign(img) * (np.abs(img) ** (1/2))
    try:
        img = cv2.resize(img, dsize=(w, h))
        np.save(normal_np_dir + save_name, img)
    except cv2.error as e:
        print(f"{name}: {e}")

    percentiles = np.percentile(img, q)
    if percentiles is not None:
        normal_p.append(percentiles)
        normal_d.append(date)


percentile_dir = "DATA/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

np.save(f"{percentile_dir}{mode}_normal_p", normal_p)
np.save(f"{percentile_dir}{mode}_normal_d", normal_d)
