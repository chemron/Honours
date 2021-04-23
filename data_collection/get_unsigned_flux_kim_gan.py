from pixel_area import get_pixel_areas
from normalise_HMI_p import clip_max
import numpy as np
from astropy.io import fits
from datetime import datetime as dt
import os

main_dir = "/home/csmi0005/Mona0028/adonea/cameron/Honours/"
folder = f"{main_dir}kim_gan/RESULTS/P100_4/STEREO_to_MAG/ITER0300000/"
save_dir = "DATA/unsigned_flux/"
os.makedirs(save_dir) if not os.path.exists(save_dir) else None
save_file = f"{save_dir}unsigned_flux_gan"
mode = "ste_full"
mode_str = "MAG_*"
shape = (1024, 1024)

header_ref = f"{main_dir}DATA/TEST/2011.11.01_00:00:00/ste_header"

def get_date_str(filename):
    date_str_in = "MAG_%Y.%m.%d_%H:%M:%S.npy"
    date_str_out = "%Y-%m-%dT%H:%M:%S.000"
    date = dt.strptime(filename, date_str_in)
    date_str = date.strftime(date_str_out)

    return date_str


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


files = np.sort(os.listdir(folder))
for i in range(len(files)):
    file = files[i]
    print(i, file)
    data = np.load(folder + file)

    # undo normalisation
    data = np.abs(data)**2
    data *= clip_max

    flux = area * np.absolute(data)

    # remove nans
    flux = np.nan_to_num(flux)

    total_flux = np.sum(flux)

    date_str = get_date_str(file)

    f = open(f"{save_file}_{mode}.txt", "a+")
    f.write(f"{date_str}\t{total_flux}\n")
    f.close()
