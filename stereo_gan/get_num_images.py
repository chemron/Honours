import numpy as np
import os
import glob
import time
from random import shuffle
from datetime import datetime, timedelta
import argparse


DATA_path = "/home/csmi0005/Mona0028/adonea/cameron/Honours/DATA/TRAIN/"


def GET_DATE(file):
    filename = file.split("/")[-1]  # filename is at end of file path
    date_str = filename.split("_")  # date string is after first "_"
    date_str = date_str[-2] + date_str[-1]
    date = datetime.strptime(date_str, "%Y.%m.%d%H:%M:%S.npy")
    return date


def GRAB_DATA(folders, tolerance=timedelta(days=3)):
    for folder in folders:
        smap = glob.glob(f"{folder}/smap_*.npy")
        mag = glob.glob(f"{folder}/MAG_*.npy")
        if len(mag) == 0 or len(smap) == 0:
            continue
        smap = smap[0]
        mag = mag[0]
        smap_date = GET_DATE(smap)
        mag_date = GET_DATE(mag)
        if abs(smap_date - mag_date) > tolerance:
            continue
        yield (smap, mag)


DATA_LIST = glob.glob(DATA_path + "*")
LIST_TOTAL = list(GRAB_DATA(DATA_LIST, tolerance=timedelta(days=7)))
LIST_TOTAL.sort()
print(LIST_TOTAL[0], LIST_TOTAL[-1])
print(f"Training on {len(LIST_TOTAL)} images.")
