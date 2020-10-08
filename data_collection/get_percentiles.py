import os
import numpy as np
from astropy.io import fits
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data",
                    help="name of data",
                    default='AIA'
                    )
args = parser.parse_args()

name = args.data
fits_dir = f"DATA/fits_{name}/"
files = os.listdir(fits_dir)
dates = []
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]


def get_percentiles(filename):
    try:
        hdul = fits.open(fits_dir + filename)
        hdul.verify("fix")
        data = hdul[1].data
        if data is not None:
            append_date(filename)
            percentiles = np.percentile(np.nan_to_num(data).flatten(), q)
            return percentiles
    except TypeError:
        print(f"TypeError:{filename}")
    except OSError:
        print(f"OSError:{filename}")
    except ValueError:
        print(f"ValueError:{filename}")
    except IndexError:
        print(f"IndexError:{filename}")


def append_date(filename):
    date_str = filename.strip('.fts').strip(".fits")
    date_str = date_str.replace(".", "").replace(":", "")
    date_str = date_str.split("_")
    if name == "AIA" or name == "HMI":
        # date string is after first "_"
        date_str = date_str[1] + date_str[2]
    elif name == "stereo":
        date_str = date_str[0] + date_str[1]
    elif name == "phase_maps":
        date_str = date_str[2] + date_str[3]
    dates.append(date_str)


files = np.sort(os.listdir(fits_dir))
percentiles = np.stack([p for f in files
                        if (p := get_percentiles(f)) is not None])

assert len(percentiles) == len(dates)
np.save(f"DATA/{name}_percentiles", percentiles)
np.save(f"DATA/{name}_dates", dates)
