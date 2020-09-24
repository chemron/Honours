from PIL import Image
from astropy.io import fits
import numpy as np
import os
import sunpy
import sunpy.map
import astropy.units as u
from astropy.coordinates import SkyCoord
import argparse
import random
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

parser.add_argument("--random",
                    help="randomly assign upper bound pixel value for AIA",
                    action="store_true"
                    )

parser.add_argument("--name",
                    help="name of folder for AIA to be saved in",
                    default="AIA")

args = parser.parse_args()


input = 'AIA'
output = 'HMI'
w = h = 1024  # desired width and height of png
m_max = 100  # maximum value for magnetograms
m_min = -100  # minimum value for magnetograms
a_min = args.min
a_max = args.max
AIA = True
HMI = False


def save_to_png(name, fits_path, png_path, min, max, w, h,
                normalise=False, rotate=False, abs=False,
                crop=False, top_right=None, bottom_left=None):
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


if __name__ == "__main__":
    # -1000 to 1000 arcsec results in a full disk image.
    # Slightly lower values will be closerto the actual edge of the Sun
    # AIA:
    if AIA:
        fits_path = "./DATA/fits_AIA/"
        png_path = "./DATA/png_aia/"

        os.makedirs(png_path) if not os.path.exists(png_path) else None

        for filename in os.listdir(fits_path):
            map_ref = sunpy.map.Map(f"{fits_path}{filename}")
            top_right = SkyCoord(1000 * u.arcsec, 1000 * u.arcsec,
                                 frame=map_ref.coordinate_frame)
            bottom_left = SkyCoord(-1000 * u.arcsec, -1000 * u.arcsec,
                                   frame=map_ref.coordinate_frame)

            # date = datetime.strptime(filename, "AIA_%Y.%m.%d_%H:%M:%S.fits")

            if args.random:
                a_max = random.random()*1800 + 200
            save_to_png(name=filename[:-5],
                        fits_path=fits_path,
                        png_path=png_path,
                        min=a_min,
                        max=a_max,
                        w=w,
                        h=h,
                        normalise=False,
                        crop=True,
                        top_right=top_right,
                        bottom_left=bottom_left
                        )
    # HMI:
    if HMI:
        fits_path = "FITS_DATA/" + output + '/'
        test_path = "DATA/TEST/" + output + '/'
        train_path = "DATA/TRAIN/" + output + '/'
        # make directories if they don't exist
        os.makedirs(test_path) if not os.path.exists(test_path) else None
        os.makedirs(train_path) if not os.path.exists(train_path) else None

        for filename in os.listdir(fits_path):
            file_info = filename.split('.')
            date = file_info[2].replace('-', '')
            month = date[4:6]
            if month == '09' or month == '10':
                png_path = test_path
            else:
                png_path = train_path
            save_to_png(name=filename[:-5],
                        fits_path=fits_path,
                        png_path=png_path,
                        min=m_min,
                        max=m_max,
                        w=w,
                        h=h,
                        rotate=True,
                        abs=abs,
                        crop=True,
                        top_right=top_right,
                        bottom_left=bottom_left
                        )
