import os
import argparse
from datetime import datetime
import numpy as np
from imageio import imread


parser = argparse.ArgumentParser()
parser.add_argument("--input",
                    help="input folder of pngs",
                    default="../data_collection/DATA/png_hmi/"
                    )
parser.add_argument("--train",
                    help="folder for training pngs",
                    default=None
                    )
parser.add_argument("--test",
                    help="folder for training pngs",
                    default="./DATA/hmi_test/"
                    )

args = parser.parse_args()

input_folder = args.input
train_folder = args.train
test_folder = args.test
test_months = (11, 12)


def save_array(input, output):
    img = imread(input)
    np.save(output, img)


# make folders
if train_folder is not None:
    os.makedirs(train_folder) if not os.path.exists(train_folder) else None
os.makedirs(test_folder) if not os.path.exists(test_folder) else None

files = np.sort(os.listdir(input_folder))

for png in files:
    info = png.split("_")
    date = f"{info[1]}_{info[2][:8]}"
    date = datetime.strptime(date, "%Y.%m.%d_%H:%M:%S")
    if (date.month in test_months) or (train_folder is None):
        output_file = test_folder + png[:-4]
    else:
        output_file = train_folder + png[:-4]

    input_file = input_folder + png

    save_array(input_file, output_file)
