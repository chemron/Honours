from pixel_area import get_pixel_areas
from normalise_HMI_p import clip_max
import numpy as np
from astropy.io import fits
from datetime import datetime as dt
import os
import glob

folders = ["../DATA/TRAIN/"]  # , "../DATA/TEST/"]
main_dir = "/home/csmi0005/Mona0028/adonea/cameron/Honours/"
save_dir = f"DATA/unsigned_flux/"
os.makedirs(save_dir) if not os.path.exists(save_dir) else None
save_file = f"{save_dir}unsigned_flux_gan"
modes = ["16_kernal_size_train"]
mode_strs = ["P100_16_kernal/*" ]
shape = (1024, 1024)
header_ref = f"{main_dir}DATA/TEST/2011.11.01_00:00:00/ste_header"


def get_date_str(filename):
    # remove directory information and .npy suffix
    f = filename.split("/")[-1][:-4]
    # date and time are on the end of string
    day, time = f.split("_")[-2:]
    date_str = day + time
    # date string formats
    date_str_in = "%Y.%m.%d%H:%M:%S"
    date_str_out = "%Y-%m-%dT%H:%M:%S.000"
    date = dt.strptime(date_str, date_str_in)
    date_str = date.strftime(date_str_out)

    return date_str


# get pixel area
hdul = fits.open(header_ref, memmap=False, ext=0)
hdul.verify("fix")
header = hdul[0].header
# radius of sun in arcsec
r_sun_arc = header["RSUN"]
# radius of sun in pixels
r_sun_pix = [0.5 * shape[0], 0.5 * shape[1]]
# width of pixel in arcsec
cdelt = [r_sun_arc/r_sun_pix[0], r_sun_arc/r_sun_pix[1]]
# reference pixel
c_ref = [0.5 * shape[0], 0.5 * shape[1]]

area = get_pixel_areas(header, shape, cdelt, c_ref)

for folder in folders:
    for date in np.sort(os.listdir(folder)):
        for i in range(len(modes)):
            mode = modes[i]
            mode_str = mode_strs[i]
            data_string = f"{folder}{date}/{mode_str}"
            print(data_string)
            data_file = glob.glob(data_string)
            if len(data_file) == 0:
                continue
            data_file = data_file[0]

            data = np.load(data_file)

            # undo normalisation
            data = np.abs(data)**2
            data *= clip_max
            flux = area * np.absolute(data)

            # remove nans
            flux = np.nan_to_num(flux)

            total_flux = np.sum(flux)

            date_str = get_date_str(data_file)

            f = open(f"{save_file}_{mode}.txt", "a+")
            f.write(f"{date_str}\t{total_flux}\n")
            f.close()
