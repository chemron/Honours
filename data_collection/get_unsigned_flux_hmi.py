from pixel_area import get_pixel_areas
import numpy as np
from astropy.io import fits
import os


# parameters

folder = "DATA/fits_HMI/"
save_folder = "DATA/unsigned_flux/"
os.makedirs(save_folder) if not os.path.exists(save_folder) else None
save_file = f"{save_folder}unsigned_flux_hmi.txt"
if os.path.exists(save_file):
    print(f"File {save_file} already exists. Removing now.")
    os.remove(save_file)


for file in np.sort(os.listdir(folder)):
    try:
        # open fits file
        hdul = fits.open(folder + file, memmap=False, ext=0)
        hdul.verify("fix")
        
        # get data and header
        data = hdul[1].data
        header = hdul[1].header
        
        # image dimensions
        shape = data.shape

        area = get_pixel_areas(header, shape)

        
        flux = area * np.absolute(data)

        # remove nans
        flux = np.nan_to_num(flux)

        total_flux = np.sum(flux)

        date_str = header["DATE-OBS"]
        
        f = open(save_file, "a+")
        f.write(f"{date_str}\t{total_flux}\n")
        f.close()
    except Exception as e:
        # This is obviously bad practice, but since I'm running this overnight I
        # don't want it to halt for some error I didn't anticipate
        print(f"Got error for file: {file}")
        print(e)


