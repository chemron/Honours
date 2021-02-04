import os
import numpy as np
from astropy.io import fits
from get_equivalent_time import get_stereo_time
from bisect import bisect_left
from datetime import datetime, timedelta


main_dir = "/home/adonea/Mona0028/adonea/cameron/Honours/"
data_dir = main_dir + "data_collection/DATA/"
stereo_fits_dir = data_dir + "fits_stereo/"
stereo_np_dir = data_dir + "np_STEREO_normalised/"
smap_fits_dir = data_dir + "fits_phase_map"


def get_stereo_header(filename):
    hdul = fits.open(stereo_fits_dir + filename, memmap=False, ext=0)
    hdul.verify("fix")
    stereo_header = hdul[0].header
    return stereo_header


def get_date(filename, mode):
    if mode == "stereo_np":
        fmt = "%Y%m%d_%H%M%S_n5eua.npy"
    elif mode == "stereo_fits":
        fmt = "%Y%m%d_%H%M%S_n5eua.fts"
    elif mode == "seismic_fits":
        fmt = "PHASE_MAP_%Y.%m.%d_%H:%M:%S.fits"
    else:
        raise ValueError(f"mode must be one of \"stereo_np\", \"stereo_fits\","
                         f" or \"seismic_fits\" not \"{mode}\"")
    return datetime.strptime(filename, fmt)


def get_filename(date, mode):
    if mode == "stereo_np":
        fmt = "%Y%m%d_%H%M%S_n5eua.npy"
    elif mode == "stereo_fits":
        fmt = "%Y%m%d_%H%M%S_n5eua.fts"
    elif mode == "seismic_fits":
        fmt = "PHASE_MAP_%Y.%m.%d_%H:%M:%S.fits"
    else:
        raise ValueError(f"mode must be one of \"stereo_np\", \"stereo_fits\","
                         f" or \"seismic_fits\" not \"{mode}\"")
    return date.strftime(fmt)


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
    Phi_c = (Phi + L_0)%(2*np.pi)
    return (Theta, Phi_c)


def get_closest(dates, date):
    pos = bisect_left(dates, date)
    if pos == 0:
        return dates[0]
    if pos == len(dates):
        return dates[-1]
    before = dates[pos - 1]
    after = dates[pos]
    if after - date < date - before:
        return after
    else:
        return before


smap_files = np.sort(os.listdir(smap_fits_dir))
stereo_files = np.sort(os.listdir(stereo_np_dir))
stereo_dates = [get_date(f, "stereo_fits") for f in stereo_files]
for filename in smap_files:
    smap_date = get_date(filename, "seismic_fits")
    ideal_stereo_date = get_stereo_time(smap_date)
    # ignore if it has rotated more than ~ 90deg between stereo and farside
    # TODO: justify the 7 days
    if abs(smap_date - ideal_stereo_date) > timedelta(days=7):
        continue

    actual_stereo_date = get_closest(ideal_stereo_date)
    # ignore if actual stereo date is off by > 2 hours
    if abs(ideal_stereo_date - actual_stereo_date) > timedelta(hours=2):
        continue

    stereo_np_name = get_filename(actual_stereo_date, "stereo_np")
    stereo_fits_name = get_filename(actual_stereo_date, "stereo_fits")

    # make group directory
    date_str = smap_date.strftime("%Y.%m.%d_%H:%M:%S")
    group_dir = f"{main_dir}DATA/{date_str}"
    os.makedirs(group_dir)

    # move stereo numpy file to DATA folder.
    os.rename(stereo_np_dir + stereo_np_name, group_dir + stereo_np_name)
    
    # move phase_map

    # save stereo header to 


# r_sun = stereo_header["RSUN"]  # radius of image of sun [arcsec]
# Phi_0 = 0  # set longetiude of observer to 0
# B_0 = stereo_header["HGLT_OBS"] * np.pi/180  # latitude of observer [rad]
# D_0 = stereo_header["DSUN_OBS"] / 696340000  # Distance to Sun [solar radii]
# stereo_header.tofile("ste_header")
# h = fits.open("ste_header")[0].header
