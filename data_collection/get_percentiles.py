import os
import numpy as np
from astropy.io import fits

fits_dir = "DATA/fits_AIA/"
files = os.listdir(fits_dir)
dates = []
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]


def get_data(filename):
    try:
        hdul = fits.open(fits_dir + filename)
        hdul.verify("fix")
        data = hdul[1].data
        if data is not None:
            append_date(filename)
            return data.flatten()
    except TypeError:
        pass


def append_date(filename):
    date_str = filename.split("_")  # date string is after first "_"
    date_str = date_str[1] + date_str[2][:-5]
    dates.append(date_str)


data_cube = np.stack([data for filename in np.sort(os.listdir(fits_dir)) if (data:=get_data(filename)) is not None])

assert len(data_cube) == len(dates)
np.save("DATA/data_cube", data_cube)
percentiles = np.percentile(data_cube, q, axis=1)
np.save("DATA/percentiles", percentiles)
np.save("DATA/dates", dates)
