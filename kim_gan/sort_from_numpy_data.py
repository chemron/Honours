import os
import argparse
from datetime import datetime
import numpy as np
from shutil import copyfile

parser = argparse.ArgumentParser()
parser.add_argument("--input",
                    help="name of data",
                    default="AIA"
                    )
parser.add_argument("--test_only",
                    action="store_true"
                    )
parser.add_argument("--func",
                    default=""
                    )
args = parser.parse_args()
func = args.func
input_folder = f"../data_collection/DATA/np_{args.input}_normalised/"  # {func}/"
if args.test_only:
    train_folder = None
else:
    train_folder = f"./DATA/{args.input.lower()}_train{func}/"

test_folder = f"./DATA/{args.input.lower()}_test{func}/"
test_months = (11, 12)

# make folders
if train_folder is not None:
    os.makedirs(train_folder) if not os.path.exists(train_folder) else None
os.makedirs(test_folder) if not os.path.exists(test_folder) else None

files = np.sort(os.listdir(input_folder))

for img in files:
    info = img.split("_")
    date = f"{info[1]}_{info[2][:8]}"
    date = datetime.strptime(date, "%Y.%m.%d_%H:%M:%S")
    if (date.month in test_months) or (train_folder is None):
        output_file = test_folder + img
    else:
        output_file = train_folder + img

    input_file = input_folder + img

    copyfile(input_file, output_file)
