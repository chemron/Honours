from pixel_area import get_pixel_areas
from normalise_HMI_p import clip_max
import numpy as np
from astropy.io import fits
import os
import glob

folders = ["../DATA/TEST/", "../DATA/TRAIN/"]
save_dir = "DATA/unsigned_flux/"
os.makedirs(save_dir) if not os.path.exists(save_dir) else None
save_file = f"{save_dir}unsigned_flux_gan"
modes = ["batch", "default", "low_tol", "ste"]
mode_strs = ["p100_batch_1/100000*", "P100_default/200000*", "P100_low_tol/200000*", "MAG_*" ]

for mode in modes:
    save_str = f"{save_file}_{mode}.txt"
    if os.path.exists(save_str):
        print(f"File {save_str} already exists. Removing now.")
        os.remove(save_str)

for folder in folders:
    for date in np.sort(os.listdir(folder)):
        try:
            hdul = fits.open(f"{folder}{date}/ste_header", memmap=False, ext=0)
            hdul.verify("fix")
            header = hdul[0].header
            for i in range(len(modes)):
                mode = modes[i]
                mode_str = mode_strs[i]
                data_file = glob.glob(f"{folder}{date}/{mode_str}")[0]
                data = np.load(data_file)

                # undo normalisation
                data = np.abs(data)**2
                data *= clip_max

                shape = data.shape

                # radius of sun in arcsec
                r_sun_arc = header["RSUN"]
                # radius of sun in pixels
                r_sun_pix = [0.5 * shape[0], 0.5 * shape[1]]
                
                cdelt = [r_sun_arc/r_sun_pix[0], r_sun_arc/r_sun_pix[1]]
                
                # reference pixel
                c_ref = [0.5 * shape[0], 0.5 * shape[1]]

                area = get_pixel_areas(header, shape, cdelt, c_ref)
                flux = area * np.absolute(data)

                # remove nans
                flux = np.nan_to_num(flux)

                total_flux = np.sum(flux)

                date_str = header["DATE-OBS"]

                f = open(f"{save_file}_{mode}.txt", "a+")
                f.write(f"{date_str}\t{total_flux}\n")
                f.close()
        except Exception as e:
            # This is obviously bad practice, but since I'm running this overnight I
            # don't want it to halt for some error I didn't anticipate
            print(f"Got error for date: {date}")
            print(e)
