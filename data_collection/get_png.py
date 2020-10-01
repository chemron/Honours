from PIL import Image
import numpy as np
import os
import sunpy
import sunpy.map
from astropy.coordinates import SkyCoord
import argparse
from multiprocessing import Pool, cpu_count


print("starting")
# from datetime import datetime

# parse the optional arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--min",
                    help="lower bound cutoff pixel value for AIA",
                    type=int,
                    default=0
                    )

parser.add_argument("--name",
                    help="name of folder for AIA to be saved in",
                    default="AIA")

args = parser.parse_args()


w = h = 1024  # desired width and height of png
name = args.name

n_cpus = min(cpu_count(), 8)


def save_to_png(name, fits_path, png_path, min, w, h):
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

    image_data -= min

    max = np.percentile(image_data, 50)*15

    image_data = np.clip(image_data, 0, max)

    # normalise data so it's between (0, 1):
    image_data = image_data/max

    # format data, and convert to image
    image = Image.fromarray(np.uint8(image_data * 255), 'L')
    # resize to width x height
    image = image.resize((w, h), Image.LANCZOS)

    image.save(png_path + name + ".png")


def catch(name, fits_path, png_path, min, w, h):
    try:
        save_to_png(name,
                    fits_path,
                    png_path,
                    min,
                    w,
                    h)
    except TypeError as err:
        f1.write(f"{filename}\t{err}\n")
    except OSError as err:
        f2.write(f"{filename}\t{err}\n")
    except IndexError as err:
        f3.write(f"{filename}\t{err}\n")
    except ValueError as err:
        f4.write(f"{filename}\t{err}\n")



fits_path = f"./DATA/fits_{name}/"
png_path = f"./DATA/png_{name.lower()}/"

error_path = "./DATA/error_handling/"
os.makedirs(error_path) if not os.path.exists(error_path) else None
os.makedirs(png_path) if not os.path.exists(png_path) else None
f1 = open(f"{error_path}TypeError.txt", 'a+')
f2 = open(f"{error_path}OSError.txt", 'a+')
f3 = open(f"{error_path}IndexError.txt", 'a+')
f4 = open(f"{error_path}ValueError.txt", 'a+')

already_downloaded = os.listdir(png_path)

files = np.sort(os.listdir(fits_path))
n = len(files)

print("starting")
inputs = []

for filename in files:
    if (filename[:-5] + ".png") not in already_downloaded:
        inputs.append((filename[:-5],
                       fits_path,
                       png_path,
                       args.min,
                       w,
                       h))
    else:
        print("already downloaded")

print(f"downloading {len(inputs)} files with {n_cpus} cpus.")
pool = Pool(n_cpus)
pool.starmap(catch, inputs)

f1.close()
f2.close()
f3.close()
