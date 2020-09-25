from PIL import Image
import numpy as np
import os
import sunpy
import sunpy.map
from astropy.coordinates import SkyCoord
import argparse
from multiprocessing import Pool, cpu_count

# from datetime import datetime

# parse the optional arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--min",
                    help="lower bound cutoff pixel value for AIA",
                    type=int,
                    default=0
                    )
parser.add_argument("--max",
                    help="upper bound cutoff pixel value for AIA",
                    type=int,
                    default=800
                    )

parser.add_argument("--name",
                    help="name of folder for AIA to be saved in",
                    default="AIA")

args = parser.parse_args()


w = h = 1024  # desired width and height of png
name = args.name


def save_to_png(name, fits_path, png_path, min, max, w, h):
    filename = fits_path + name + ".fits"
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
    image_data = np.clip(image_data, min, max)
    # translate data so it's between (0, max-min):
    image_data -= min
    # normalise data so it's between (0, 1):
    image_data = image_data/(max - min)

    # format data, and convert to image
    image = Image.fromarray(np.uint8(image_data * 255), 'L')
    # resize to width x height
    image = image.resize((w, h), Image.LANCZOS)

    image.save(png_path + name + ".png")


fits_path = f"./DATA/fits_{name}/"
png_path = f"./DATA/png_{name.lower()}/"

os.makedirs(png_path) if not os.path.exists(png_path) else None
files = np.sorted(os.listdir(fits_path))
n = len(files)
for i in range(0, n, 20) in files:
    end = min(n, i + 20)
    current = files[i:end]
    
    save_to_png(name=filename[:-5],
                fits_path=fits_path,
                png_path=png_path,
                min=args.min,
                max=args.max,
                w=w,
                h=h)
