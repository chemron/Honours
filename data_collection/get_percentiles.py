import os
import numpy as np
import sunpy
import sunpy.map
from astropy.coordinates import SkyCoord
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data",
                    help="name of data",
                    default='AIA'
                    )
args = parser.parse_args()

mode = args.data
fits_dir = f"DATA/fits_{mode}/"
np_dir = f"DATA/np_{mode}/"
os.makedirs(np_dir) if not os.path.exists(np_dir) else None
already_done = os.listdir(np_dir)
files = np.sort(os.listdir(fits_dir))
dates = []
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]


def get_percentiles(filename):
    try:
        name = filename.strip(".fits").strip('.fts')
        if name + ".npy" in already_done:
            print(f"Already converted: {name}")
            data = np.load(f"{np_dir}{name}.npy").flatten()
        else:
            print(filename)
            map_ref = sunpy.map.Map(fits_dir + filename)

            # not necessary for percentiles
            mat = map_ref.rotation_matrix
            map_ref = map_ref.rotate(rmatrix=mat)

            # crop so only sun is shown
            radius = map_ref.rsun_obs
            top_right = SkyCoord(radius, radius,
                                 frame=map_ref.coordinate_frame)
            bottom_left = SkyCoord(-radius, -radius,
                                   frame=map_ref.coordinate_frame)
            submap = map_ref.submap(bottom_left, top_right)

            data = submap.data
            if data is not None:
                np.save(f"{np_dir}{name}", data)
                data = np.nan_to_num(data).flatten()
            else:
                return

        percentiles = np.percentile(data, q)
        if percentiles is not None:
            append_date(name)
            return percentiles
    except TypeError as err:
        print(f"TypeError:{filename}, {err}")
    except OSError as err:
        print(f"OSError:{filename}, {err}")
    except ValueError as err:
        print(f"ValueError:{filename}, {err}")
    except IndexError as err:
        print(f"IndexError:{filename}, {err}")
    return


def append_date(name):
    date_str = name.replace(".", "").replace(":", "")
    date_str = date_str.split("_")
    if mode == "AIA" or mode == "HMI":
        # date string is after first "_"
        date_str = date_str[1] + date_str[2]
    elif mode == "stereo":
        date_str = date_str[0] + date_str[1]
    elif mode == "phase_map":
        date_str = date_str[2] + date_str[3]
    dates.append(date_str)


files = np.sort(os.listdir(fits_dir))

percentiles = np.stack([p for f in files
                        if (p := get_percentiles(f)) is not None])

if len(percentiles) != len(dates):
    print(len(percentiles), len(dates))
    raise Exception("percentiles and dates have different sizes")

percentile_dir = "DATA/np_objects/"
os.makedirs(percentile_dir) if not os.path.exists(percentile_dir) else None

np.save(f"{percentile_dir}{mode}_percentiles", percentiles)
np.save(f"{percentile_dir}{mode}_dates", dates)
