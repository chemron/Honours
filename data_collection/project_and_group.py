import os
import numpy as np
from astropy.io import fits
from get_equivalent_time import get_stereo_time
from bisect import bisect_left
from datetime import datetime, timedelta
from shutil import copyfile
from skimage.transform import warp
import matplotlib.pyplot as plt
import glob


main_dir = "/home/adonea/Mona0028/adonea/cameron/Honours/"
# main_dir = "../"
data_dir = main_dir + "data_collection/DATA/"
stereo_fits_dir = data_dir + "fits_STEREO/"
stereo_np_dir = data_dir + "np_STEREO_normalised/"
smap_fits_dir = data_dir + "fits_phase_map/"
model = "P100_4/"
mode = "STEREO_to_MAG/ITER0300000/"
stereo_mag_dir = f"{main_dir}kim_gan/RESULTS/{model}{mode}"


def get_stereo_header(filename):
    hdul = fits.open(stereo_fits_dir + filename, memmap=False, ext=0)
    hdul.verify("fix")
    stereo_header = hdul[0].header
    return stereo_header


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


def get_filename(date, mode):
    if mode == "stereo_np":
        fmt = "STE_%Y.%m.%d_%H:%M:%S.npy"
    elif mode == "stereo_mag":
        fmt = "MAG_%Y.%m.%d_%H:%M:%S.npy"
    elif mode == "stereo_fits":
        fmt = "%Y%m%d_%H%M%S*"
    elif mode == "seismic_fits":
        fmt = "PHASE_MAP_%Y.%m.%d_%H:%M:%S.fits"
    else:
        raise ValueError(f"mode must be one of \"stereo_np\", stereo_mag,"
                         f"\"stereo_fits\", or \"seismic_fits\" not"
                         f"\"{mode}\"")
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
stereo_dates = [get_date(f, "stereo_np") for f in stereo_files]
for smap_file in smap_files:
    # make group directory
    smap_date = get_date(smap_file, "seismic_fits")
    smap_date_str = smap_date.strftime("%Y.%m.%d_%H:%M:%S")
    print(smap_date_str)
    group_dir = f"{main_dir}DATA/{smap_date_str}/"
    if os.path.exists(group_dir):
        continue
        print("group already exists")

    ideal_stereo_date = get_stereo_time(smap_date)
    # ignore if it has rotated more than ~ 90deg between stereo and farside
    # TODO: justify the 7 days
    time_delay = abs(smap_date - ideal_stereo_date)
    if time_delay > timedelta(days=7):
        print(f"Time delay of {time_delay} (>7 day) time delay. Skipping File")
        continue

    actual_stereo_date = get_closest(stereo_dates, ideal_stereo_date)
    # ignore if actual stereo date is off by > 2 hours
    if abs(ideal_stereo_date - actual_stereo_date) > timedelta(hours=2):
        print("Closest match is off by ")
        continue

    os.makedirs(group_dir)

    stereo_np_name = get_filename(actual_stereo_date, "stereo_np")
    stereo_mag_name = get_filename(actual_stereo_date, "stereo_mag")

    stereo_data = np.load(f"{stereo_np_dir}{stereo_np_name}")
    stereo_fits_name = get_filename(actual_stereo_date, "stereo_fits")
    # use glob to get suffix correct
    stereo_fits_path = glob.glob(stereo_fits_dir + stereo_fits_name)[0]

    # move stereo numpy file to DATA folder.
    # os.rename(stereo_np_dir + stereo_np_name, group_dir + stereo_np_name)
    copyfile(stereo_np_dir + stereo_np_name, group_dir + stereo_np_name)

    # get stereo header
    hdul = fits.open(stereo_fits_path, memmap=False, ext=0)
    hdul.verify("fix")
    stereo_header = hdul[0].header
    stereo_header.tofile(f"{group_dir}ste_header", overwrite=True)
    # h = fits.open("ste_header")[0].header

    # get sesmic map data and header
    hdul = fits.open(smap_fits_dir + smap_file, memmap=False, ext=0)
    hdul.verify("fix")
    smap_data = hdul[0].data
    smap_header = hdul[0].header

    # save seismic map header
    smap_header.tofile(f"{group_dir}smap_header", overwrite=True)

    # get parameters
    L_0 = smap_header["REF_L0"] * np.pi/180
    B_0 = smap_header["REF_B0"] * np.pi/180
    r_sun = stereo_header["RSUN"]
    Phi_0 = 0
    B_0 = stereo_header["HGLT_OBS"] * np.pi/180
    D_0 = stereo_header["DSUN_OBS"] / 696340000  # in terms of radius

    map_args = {"r_sun": r_sun, "D_0": D_0, "R_0": 1,
                "B_0": B_0,  "Phi_0": Phi_0, "L_0": L_0}

    # transform seismic map to match stereo data:
    new_smap = warp(smap_data, transformation,
                    output_shape=(1024, 1024), map_args=map_args)
    np.save(f"{group_dir}smap_{smap_date_str}.npy", new_smap)

    # copy over stereo magnetograms
    copyfile(stereo_mag_dir + stereo_mag_name, group_dir + stereo_mag_name)
    stereo_mag_data = np.load(stereo_mag_dir + stereo_mag_name)

    # make plot
    plt.figure(1, figsize=(20, 5))
    plt.subplot(141)
    plt.imshow(stereo_data, origin="lower")
    plt.subplot(142)
    plt.imshow(new_smap, origin="lower")
    plt.subplot(143)
    plt.imshow(stereo_mag_data, origin="lower")
    plt.subplot(144)
    plt.imshow(stereo_data, origin="lower", alpha=0.55)
    plt.imshow(new_smap, origin="lower", alpha=0.55)
    plt.imshow(stereo_mag_data, origin="lower", alpha=0.55)
    plt.tight_layout
    plt.savefig(f"{group_dir}comparison.png")
    plt.close(1)
