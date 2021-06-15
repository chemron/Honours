import os
import numpy as np
from astropy.io import fits
from get_equivalent_time import get_stereo_time
from bisect import bisect_left
from datetime import datetime, timedelta
from shutil import copyfile, rmtree
from skimage.transform import warp
import matplotlib.pyplot as plt
import glob

main_dir = "/home/csmi0005/Mona0028/adonea/cameron/Honours/"
data_dir = main_dir + "data_collection/DATA/"
smap_fits_dir = data_dir + "fits_phase_map/"
output_dir = data_dir + "np_phase_projected/"
header_ref = f"{main_dir}DATA/TEST/2011.11.01_00:00:00/ste_header"


def get_date(filename, mode):
    if mode == "stereo_np":
        fmt = "STE_%Y.%m.%d_%H:%M:%S.npy"
    elif mode == "stereo_fits":
        filename = filename.split[0] + filename.split[1]
        fmt = "%Y%m%d_%H%M%S"
    elif mode == "seismic_fits":
        fmt = "PHASE_MAP_%Y.%m.%d_%H:%M:%S.fits"
    else:
        raise ValueError(f"mode must be one of \"stereo_np\", \"stereo_fits\","
                         f" or \"seismic_fits\" not \"{mode}\"")
    return datetime.strptime(filename, fmt)


def get_distance(theta_x, theta_y, D_0=200, R_0=1):
    # initialise d
    d = np.ones(theta_x.shape)

    cos_theta = np.sin(np.pi/2 - theta_y) * np.cos(theta_x)
    # descriminant in distance formula
    des = D_0**2 * cos_theta**2 - D_0**2 + R_0

    # if no solution (point not on sun) return Nan
    d[des < 0] = np.nan
    # use minus since we want the hemisphere facing us
    d *= D_0 * cos_theta - np.sqrt(D_0**2 * cos_theta**2 - D_0**2 + R_0)

    return d


def heliop_to_helioc(theta_x, theta_y, D_0=200):
    """
    Theta_x/y in arcsec
    d in solar radii
    """
    # convert to radians
    theta_y = theta_y * np.pi / (180 * 3600)
    theta_x = theta_x * np.pi / (180 * 3600)
    d = get_distance(theta_x, theta_y, D_0)
    x = d * np.cos(theta_y) * np.sin(theta_x)
    y = d * np.sin(theta_y)
    z = D_0 - d * np.cos(theta_y) * np.cos(theta_x)

    return (x, y, z)


def helioc_to_heliographic(x, y, z, B_0=0, Phi_0=0, R_0=1, L_0=0):
    r = R_0
    Theta = np.arcsin((y*np.cos(B_0) + z*np.sin(B_0))/r)
    Phi = Phi_0 + np.angle(z*np.cos(B_0) - y * np.sin(B_0) + x * 1.j)
    Phi_c = (Phi + L_0) % (2*np.pi)
    return (Theta, Phi_c)


def transformation(coord, r_sun=1200, D_0=200, R_0=1, B_0=0,  Phi_0=0, L_0=0):
    col = coord[:, 0]
    row = coord[:, 1]
    w = h = 1024
    # convert col and row to helioprojective arcsec
    theta_x = (col - w/2) * 2 * r_sun / w
    theta_y = (row - h/2) * 2 * r_sun / h

    # get heliocentric coords
    x, y, z = heliop_to_helioc(theta_x, theta_y, D_0=D_0)

    Theta, Phi_c = helioc_to_heliographic(x, y, z, B_0=B_0, Phi_0=Phi_0,
                                          R_0=R_0, L_0=L_0)

    col = Phi_c * 180 / np.pi
    row = (Theta + np.pi/2) * 180 / np.pi
    return np.stack((col, row), axis=-1)




hdul = fits.open(header_ref, memmap=False, ext=0)
hdul.verify("fix")
stereo_header = hdul[0].header

smap_files = np.sort(os.listdir(smap_fits_dir))

for smap_file in smap_files:
    smap_date = get_date(smap_file, "seismic_fits")
    smap_date_str = smap_date.strftime("%Y.%m.%d_%H:%M:%S")
    # get sesmic map data and header
    hdul = fits.open(smap_fits_dir + smap_file, memmap=False, ext=0)
    hdul.verify("fix")
    smap_data = hdul[0].data
    smap_header = hdul[0].header

    # get parameters
    try:
        L_0 = smap_header["REF_L0"] * np.pi/180
        B_0 = smap_header["REF_B0"] * np.pi/180
        r_sun = stereo_header["RSUN"]
        Phi_0 = 0
        B_0 = stereo_header["HGLT_OBS"] * np.pi/180
        D_0 = stereo_header["DSUN_OBS"] / 696340000  # in terms of radius
    except TypeError:
        print("Missing args")
        continue

    map_args = {"r_sun": r_sun, "D_0": D_0, "R_0": 1,
                "B_0": B_0,  "Phi_0": Phi_0, "L_0": L_0}

    # transform seismic map to match stereo data:
    new_smap = warp(smap_data, transformation,
                    output_shape=(1024, 1024), map_args=map_args)
    np.save(f"{output_dir}smap_{smap_date_str}.npy", new_smap)