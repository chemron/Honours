#!/usr/bin/env python3
import os
import sunpy
import sunpy.map
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from PIL import Image
import argparse
from datetime import datetime, timedelta


# parse the optional arguments:
parser = argparse.ArgumentParser()
parser.add_argument("--min",
                    help="lower bound cutoff pixel value",
                    type=int,
                    default=650
                    )
parser.add_argument("--max",
                    help="upper bound cutoff pixel value",
                    type=int,
                    default=5000
                    )
parser.add_argument("--FITS_path",
                    help="directory of FITS data",
                    default="DATA/fits_stereo/"
                    )
parser.add_argument("--png_path",
                    help="name of folder to be saved in",
                    default="DATA/png_stereo/")
parser.add_argument("--times_path",
                    help="path to times document",
                    default="DATA/phase_stereo_times.txt")
parser.add_argument("--name",
                    default="stereo")

args = parser.parse_args()


def save_to_png(name, fits_path, png_path, min, max, w, h, i):

    filename = fits_path + name
    print(filename)

    s_map = sunpy.map.Map(filename)

    # rotating such that north is top of image
    mat = s_map.rotation_matrix
    s_map = s_map.rotate(rmatrix=mat)

    # radius of sun in arcseconds
    radius = s_map.rsun_arcseconds * u.arcsec

    # crop so only the sun is present
    top_right = SkyCoord(radius, radius, frame=s_map.coordinate_frame)
    bottom_left = SkyCoord(-radius, -radius, frame=s_map.coordinate_frame)
    submap = s_map.submap(bottom_left, top_right)

    # get image data
    image_data = submap.data

    # clip data
    image_data = np.clip(image_data, min, max)

    # translate data so it starts at 0
    image_data -= min

    # normalise data between 0 and 1
    image_data = image_data/((max - min))

    # format data, and convert to image
    image = Image.fromarray(np.uint8(image_data * 255), 'L')

    # resize
    image = image.resize((w, h), Image.LANCZOS)

    # date:
    y = name[:4]
    m = name[4:6]
    d = name[6:8]
    H = name[9:11]
    M = name[11:13]
    S = name[13:15]

    s_time = datetime(year=int(y),
                      month=int(m),
                      day=int(d),
                      hour=int(H),
                      minute=int(M),
                      second=int(S))

    while stereo_times[i] < s_time:
        i += 1

    if (stereo_times[i]-s_time) > (s_time - stereo_times[i-1]):
        phase_time = phase_times[i-1]
    else:
        phase_time = phase_times[i]
        i += 1

    # add an hour if time is before 12
    if phase_time.hour == 11 or phase_time.hour == 23:
        phase_time += timedelta(hours=1)

    phase_string = phase_time.strftime("%Y.%m.%d_%H:00:00")
    filename = f"{png_path}STEREO_{y}.{m}.{d}_{H}:{M}:{S}_" \
               f"{phase_string}.png"
    image.save(filename)

    return i


w = h = 1024
# min and maxed were chosen so that the result was as similar to
# aia between a min of 0 and a max of 150
min = args.min
max = args.max
fits_path = args.FITS_path
png_path = args.png_path
os.makedirs(png_path) if not os.path.exists(png_path) else None


error_path = "DATA/error_handling/"
os.makedirs(error_path) if not os.path.exists(error_path) else None
f1 = open(f"{error_path}{args.name}_ValueError.txt", 'w')

files = np.sort(os.listdir(fits_path))


# load phase and stereo time data
phase_times, stereo_times = np.loadtxt(args.times_path,
                                       dtype=str).T

phase_times = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                       for time in phase_times
                        ])


stereo_times = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                        for time in stereo_times
                         ])

# index for times
index = 0

for filename in files:
    try:
        index = save_to_png(name=filename,
                            fits_path=fits_path,
                            png_path=png_path,
                            min=min,
                            max=max,
                            w=w,
                            h=h,
                            i=index
                            )
    except ValueError as err:
        print(f"Error: {filename}")
        f1.write(f"{filename}\t{err}\n")
    except TypeError as err:
        print(f"Error: {filename}")
        f1.write(f"{filename}\t{err}\n")
    except OSError as err:
        print(f"Error: {filename}")
        f1.write(f"{filename}\t{err}\n")

f1.close()
