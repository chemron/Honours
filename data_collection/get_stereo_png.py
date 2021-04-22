#!/usr/bin/env python3
import os
import sunpy
import sunpy.map
import numpy as np
from astropy.coordinates import SkyCoord
from PIL import Image
import argparse
from multiprocessing import Pool, cpu_count


# parse the optional arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--min",
                    help="lower bound cutoff pixel value",
                    type=int,
                    default=700
                    )
parser.add_argument("--FITS_path",
                    help="directory of FITS data",
                    default="DATA/fits_stereo/"
                    )
parser.add_argument("--png_path",
                    help="name of folder to be saved in",
                    default="DATA/png_stereo/")
parser.add_argument("--name",
                    default="stereo")

args = parser.parse_args()


def save_to_png(name, fits_path, png_path, min, w, h):

    filename = fits_path + name
    print(filename)
    map_ref = sunpy.map.Map(filename)
    mat = map_ref.rotation_matrix
    map_ref = map_ref.rotate(rmatrix=mat)

    # crop so only sun is shown
    radius = map_ref.rsun_obs
    top_right = SkyCoord(radius, radius, frame=map_ref.coordinate_frame)
    bottom_left = SkyCoord(-radius, -radius, frame=map_ref.coordinate_frame)
    submap = map_ref.submap(bottom_left, top_right)
    # clip data between (min, max):
    image_data = submap.data

    image_data -= min

    max = np.percentile(image_data, 50)*15

    image_data = np.clip(image_data, 0, max)

    # normalise data so it's between (0, 1):
    image_data = image_data/max

    # format data, and convert to image
    image = Image.fromarray(np.uint8(image_data * 255), 'L')
    # resize to width x height
    image = image.resize((w, h), Image.LANCZOS)

    # date:
    y = name[:4]
    m = name[4:6]
    d = name[6:8]
    H = name[9:11]
    M = name[11:13]
    S = name[13:15]

    filename = f"{png_path}STEREO_{y}.{m}.{d}_{H}:{M}:{S}.png"
    image.save(filename)


def catch(*inputs):
    try:
        save_to_png(*inputs)
    except ValueError as err:
        print(f"Error: {filename}")
        f1.write(f"{filename}\t{err}\n")
    except TypeError as err:
        print(f"Error: {filename}")
        f1.write(f"{filename}\t{err}\n")
    except OSError as err:
        print(f"Error: {filename}")
        f1.write(f"{filename}\t{err}\n")


w = h = 1024
# min and maxed were chosen so that the result was as similar to
# aia between a min of 0 and a max of 150
min = args.min
fits_path = args.FITS_path
png_path = args.png_path
os.makedirs(png_path) if not os.path.exists(png_path) else None
n_cpus = np.min((cpu_count(), 8))
error_path = "DATA/error_handling/"
os.makedirs(error_path) if not os.path.exists(error_path) else None
f1 = open(f"{error_path}{args.name}_Error.txt", 'w')
files = np.sort(os.listdir(fits_path))


inputs = []
for filename in files:
    inputs.append((filename,
                   fits_path,
                   png_path,
                   min,
                   w,
                   h))

print(f"downloading {len(inputs)} files with {n_cpus} cpus.")
pool = Pool(n_cpus)
pool.starmap(catch, inputs)


f1.close()
