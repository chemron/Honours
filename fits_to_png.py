from PIL import Image
from astropy.io import fits
import numpy as np
import os

w = 361  # desired width and height of png
h = 181
max = 0.2  # maximum value for magnetograms
min = -0.2  # minimum value for magnetograms

# fits_path = "test_fits/"
# png_path = "test_png/"

fits_path = "fits_phase_maps/"
png_path = "png_phase_maps_shifted/"


def save_to_png(name):
    filename = fits_path + name + ".fits"
    hdul = fits.open(filename, memmap=True, ext=0)
    hdul.verify("fix")

    image_data = hdul[0].data

    # location of nans in data
    nan_loc = np.where(np.isnan(image_data))

    # location of lowest nans in image
    low_nan = (nan_loc[0] == np.max(nan_loc[0]))
    low_nan_loc = np.where(low_nan)

    # collumns of lowest nans
    low_nan_x = nan_loc[1][np.min(low_nan_loc):np.max(low_nan_loc)]

    # centre collumn:
    centre = (np.min(low_nan_x) + np.max(low_nan_x))//2

    # split into two parts:
    if centre >= w//2:
        split = np.hsplit(image_data,
                          [centre - w//2]
                          )
    else:
        split = np.hsplit(image_data,
                          [w//2 + centre]
                          )

    image_data = np.concatenate((split[1], split[0]), axis=1)

    # clip data between (min, max):
    image_data = np.clip(image_data, min, max)

    # translate data so it's between (0, max-min):
    image_data -= min
    # normalise data so it's between (0, 1):
    image_data = image_data/(max - min)

    # format data, and convert to image
    image = Image.fromarray(np.uint8(image_data * 255), 'L')

    image.save(png_path + name + ".png")


f1 = open("ValueError.txt", 'w')
f2 = open("OSError.txt", 'w')

for file in os.listdir(fits_path):
    name = file[:-5]
    try:
        save_to_png(name)
        print(name)
    except ValueError:
        f1.write(name)
    except OSError:
        f2.write(name)
