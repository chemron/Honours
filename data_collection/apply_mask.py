import glob
import numpy as np

path = "/home/adonea/Mona0028/adonea/cameron/Honours/DATA"
folders = [f"{path}/small_test"]  # , "DATA/TRAIN"]
types = ["MAG", "smap"]
size = 1024


def get_mask(size):
    w = h = size
    center = (int(w/2), int(h/2))
    radius = w/2 + 1
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    mask = dist_from_center <= radius
    return mask


for folder in folders:
    sub_folders = glob.glob(f"{folder}/*")
    mask = get_mask(size)
    for sub_folder in sub_folders:
        for type in types:
            file_str = f"{sub_folder}/{type}*.npy"
            file = glob.glob(file_str)
            if len(file) == 1:
                filename = file[0]
                arr = np.load(filename)
                arr = np.nan_to_num(arr)
                arr = mask * arr
                np.save(filename, arr)
            else:
                print(f"no files in: {file_str}")
