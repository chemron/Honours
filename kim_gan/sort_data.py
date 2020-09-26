import os
import argparse
from shutil import copyfile
from datetime import datetime
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("--input",
                    help="input folder of pngs",
                    default="../data_collection/DATA/png_aia/"
                    )
parser.add_argument("--train",
                    help="folder for training pngs",
                    default="./DATA/aia_train/"
                    )
parser.add_argument("--test",
                    help="folder for training pngs",
                    default="./DATA/aia_test/"
                    )


input_folder = args.input
train_folder = args.train
test_folder = args.test
test_months = (11, 12)

# make folders
os.makedirs(train_folder) if not os.path.exists(train_folder) else None
os.makedirs(test_folder) if not os.path.exists(test_folder) else None

files = np.sort(os.listdir(input_folder))

for png in files:
    info = png.split("_")
    date = f"{info[1]}_{info[2][:8]}"
    date = datetime.strptime(date, "%Y.%m.%d_%H:%M:%S")
    if date.month in test_months:
        output_file = test_folder + png
    else:
        output_file = train_folder + png
    
    input_file = input_folder + png
    copyfile(input_file, output_file)
