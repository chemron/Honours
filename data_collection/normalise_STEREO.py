from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
import argparse
plt.switch_backend('agg')


parser = argparse.ArgumentParser()
parser.add_argument("--data",
                    help="name of data",
                    default='STEREO'
                    )
parser.add_argument("--log",
                    action="store_true",
                    )
parser.add_argument("--just_plot",
                    action="store_true",
                    )
parser.add_argument("--func",
                    default="",
                    )
args = parser.parse_args()
mode = args.data

# moving average over 50 images
n = 50
np_dir = f"DATA/np_{mode}/"
normal_np_dir = f"DATA/np_{mode}_normalised{args.func}/"
os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None

percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
dates = np.load(f"DATA/np_objects/{mode}_dates.npy")
if mode == "STEREO":
    dates = np.apply_along_axis(lambda d: d[0] + d[1], 1, dates)

datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                  for date in dates]
# don't normalise data, just plot percentiles:
just_plot = args.just_plot
w = h = 1024  # desired width and height of output

n_ax = 6
current_ax = 0
# plot percentiles vs dates
fig, axs = plt.subplots(n_ax, 1, figsize=(10, 12), sharex=True)
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]

# raw percentiles

for i in range(len(percentiles)-1, -1, -1):
    axs[current_ax].plot_date(datetime_dates, percentiles[i],
                              label=f'${q[i]}$th percentile',
                              markersize=1)

# axs[current_ax].set_yscale('log')
axs[current_ax].set_ylim(500, 17500)

# next ax:
current_ax += 1

# zero point
zero_point = np.load("DATA/np_objects/STEREO_zeros.npy")
zero_point = np.average(zero_point)
zero_point = int(np.round(zero_point))

percentiles -= zero_point


# shifted percentiles


for i in range(len(percentiles)-1, -1, -1):
    axs[current_ax].plot_date(datetime_dates, percentiles[i],
                              label=f'${q[i]}$th percentile',
                              markersize=1)

# axs[current_ax].set_yscale('log')
axs[current_ax].set_ylim(500 - zero_point, 17500 - zero_point)
current_ax += 1

# get cutoff
upper_cutoff = np.full(len(datetime_dates), 1300)
upper_cutoff -= zero_point
lower_cutoff = np.array([1100 if (x < datetime(2014, 5, 1))
                         else 1070 if (x < datetime(2015, 8, 15))
                         else 1010 if (x < datetime(2016, 12, 1))
                         else 980 if (x < datetime(2018, 4, 1))
                         else 950 for x in datetime_dates])
lower_cutoff -= zero_point


axs[current_ax].plot_date(datetime_dates, upper_cutoff,
                          label='upper cutoff',
                          linestyle="-",
                          marker="")


axs[current_ax].plot_date(datetime_dates, lower_cutoff,
                          label='lower cutoff',
                          linestyle="-",
                          marker="")


axs[current_ax].plot_date(datetime_dates, percentiles[8],
                          label='75th percentile',
                          markersize=1)

axs[current_ax].set_ylim(900 - zero_point, 1400 - zero_point)
current_ax += 1

outlier_indicies = np.array(((percentiles[8] < lower_cutoff) |
                             (percentiles[8] > upper_cutoff)))
outlier_indicies = np.nonzero(outlier_indicies)

percentiles = np.delete(percentiles, outlier_indicies, 1)
dates = np.delete(dates, outlier_indicies)

datetime_dates = np.delete(datetime_dates, outlier_indicies[0])


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


rolling_75p = moving_average(percentiles[8], n)
rolling_dates = dates[n//2-1:-n//2]
percentiles = percentiles.T[n//2-1:-n//2].T
datetime_dates = datetime_dates[n//2-1:-n//2]
normal_percentiles = percentiles/rolling_75p
axs[current_ax].plot_date(datetime_dates, rolling_75p,
                          label=f'Rolling 75th percentile\n(over {n} images)',
                          markersize=1)
axs[current_ax].set_ylim(900 - zero_point, 1400 - zero_point)
current_ax += 1

# for i in range(len(percentiles)-1, len(percentiles)//2 - 1, -1):
#     axs[current_ax].plot_date(datetime_dates, normal_percentiles[i],
#                               label=f'${q[i]}$th percentile',
#                               markersize=1)
# axs[current_ax].set_yscale("log")

# clip max from AIA
clip_max = 110.59708760329583
normal_percentiles = normal_percentiles/clip_max

for i in range(len(percentiles)-1, len(percentiles)//2 - 1, -1):
    axs[current_ax].plot_date(datetime_dates, normal_percentiles[i],
                              label=f'${q[i]}$th percentile',
                              markersize=1)
axs[current_ax].set_ylim(0, 1)


# normal_percentiles = np.sign(normal_percentiles) * \
#                       (np.abs(normal_percentiles)**(1/2))


# for i in range(len(percentiles)-1, - 1, -1):
#     axs[current_ax].plot_date(datetime_dates, normal_percentiles[i],
#                     #  label=f'${q[i]}$th percentile',
#                      markersize=1)


# axs[current_ax].set_ylabel("Pixel Intensity")
# axs[current_ax].set_ylabel("Pixel Intensity")

# if args.log:
#     axs[current_ax].set_ylabel("Pixel Intensity (log scale)")
#     axs[current_ax].set_yscale('log')
# else:
#     axs[current_ax].set_ylabel("Pixel Intensity")

# axs[current_ax].set_ylabel("Pixel Intensity")
# axs[current_ax].set_ylabel("Pixel Intensity")
# axs[current_ax].set_ylim(0, 1)

# GET TICkS
rule = rrulewrapper(MONTHLY, interval=6)
loc = RRuleLocator(rule)
axs[-1].xaxis.set_major_locator(loc)
formatter = DateFormatter('%m/%y')
axs[-1].xaxis.set_major_formatter(formatter)
axs[-1].xaxis.set_tick_params(rotation=30, labelsize=10)
axs[-1].set_xlabel("Date")
axs[-1].set_xlim(datetime_dates[0], datetime_dates[-1])

for ax in axs:
    # Put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()

fig.savefig(f"percentile_plots/{mode}_normalising_percentiles.png"
            f"{args.func}",
            bbox_inches='tight')


# # normalise data
# data = np.sort(os.listdir(np_dir))
# data = np.delete(data, outlier_indicies)
# data = data[n//2-1:-n//2]

# print(len(data), len(rolling_75p))

# if not just_plot:
#     import cv2
#     for i in range(len(data)):
#         # what we need to divide by to normalise with clip_max at 1
#         name = data[i]
#         divider = rolling_75p[i]*clip_max
#         filename = np_dir + name
#         img = np.load(filename)
#         img = img/divider
#         img = img.clip(0, 1)
#         img = np.sign(img) * (np.abs(img) ** (1/2))
#         try:
#             img = cv2.resize(img, dsize=(w, h))
#             np.save(normal_np_dir + name, img)
#         except cv2.error as e:
#             print(f"{name}: {e}")
