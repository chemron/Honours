import numpy as np
import os
from shutil import move

dir_in = "/home/adonea/Mona0028/adonea/cameron/Honours/DATpythnA/"
dir_out_train = "/home/adonea/Mona0028/adonea/cameron/Honours/DATA/TRAIN/"
dir_out_test = "/home/adonea/Mona0028/adonea/cameron/Honours/DATA/TEST/"
for dir in (dir_out_train, dir_out_test):
    os.makedirs(dir) if not os.path.exists(dir) else None

upsample = True
test_months = (11, 12)


def is_test(filename):
    date = filename.split("_")[-2]
    month = int(date.split(".")[1])
    return month in test_months


filenames = np.sort(os.listdir(dir_in))
for filename in filenames:
    print(filename)
    path_in = dir_in + filename
    if is_test(filename):
        path_out = dir_out_test + filename
    else:
        path_out = dir_out_train + filename

    move(path_in, path_out)
