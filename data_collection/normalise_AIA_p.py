from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
from normalise_stereo_p import clip_max
plt.switch_backend('agg')


mode = 'AIA'
log = False
cam = False
func = ""
get_min_max = False

# moving average over 50 images
n = 50
np_dir = f"DATA/np_{mode}/"
normal_np_dir = f"DATA/np_{mode}_normalised{func}/"
os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None

percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
dates = np.load(f"DATA/np_objects/{mode}_dates.npy")
if mode == "STEREO":
    dates = np.apply_along_axis(lambda d: d[0] + d[1], 1, dates)

datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                  for date in dates]

w = h = 1024  # desired width and height of output

# plot percentiles vs dates
fig, axs = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
handles = []
labels = []

# cameron factor
cam_factor = percentiles[7]*15

axs[0].plot_date(datetime_dates, percentiles[8],
                 label='75th percentile',
                 markersize=1)

# get cutoff

cutoff = np.array([45 if (x < datetime(2014, 1, 1))
                   else 20 if (x < datetime(2015, 2, 1))
                   else 8 for x in datetime_dates])

axs[0].plot_date(datetime_dates, cutoff,
                 label='Outlier cutoff',
                 markersize=1)

outlier_indicies = np.nonzero(percentiles[8] < cutoff)

percentiles = np.delete(percentiles, outlier_indicies, 1)
cam_factor = np.delete(cam_factor, outlier_indicies)
dates = np.delete(dates, outlier_indicies)
datetime_dates = np.delete(datetime_dates, outlier_indicies)


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


rolling_75p = moving_average(percentiles[8], n)
rolling_dates = dates[n//2-1:-n//2]
percentiles = percentiles.T[n//2-1:-n//2].T
cam_factor = cam_factor[n//2-1:-n//2]
datetime_dates = datetime_dates[n//2-1:-n//2]
normal_percentiles = percentiles/rolling_75p
cam_normal = cam_factor/rolling_75p
axs[1].plot_date(datetime_dates, rolling_75p,
                 label=f'Rolling 75th percentile\n(over {n} images)',
                 markersize=1)


q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
for i in range(len(percentiles)-1, -1, -1):
    axs[2].plot_date(datetime_dates, normal_percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)
if cam:
    axs[2].plot_date(datetime_dates, cam_normal,
                     label='Cam factor',
                     markersize=1,
                     c='k'
                     )

# clip_max = np.max(normal_percentiles[-1][:50])
# use the average 99.99th percentile
# clip_max = np.average(normal_percentiles[-2])
# print(clip_max)
normal_percentiles = normal_percentiles.clip(None, clip_max)
cam_normal = cam_normal.clip(None, clip_max)

normal_percentiles = normal_percentiles/clip_max

for i in range(len(percentiles)-1, - 1, -1):
    axs[3].plot_date(datetime_dates, normal_percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)
if cam:
    axs[3].plot_date(datetime_dates, cam_normal,
                     label='Cam factor',
                     c='k',
                     markersize=1)


normal_percentiles = np.sign(normal_percentiles) * \
                      (np.abs(normal_percentiles)**(1/2))


for i in range(len(percentiles)-1, - 1, -1):
    axs[4].plot_date(datetime_dates, normal_percentiles[i],
                     markersize=1)


axs[0].set_ylabel("Pixel Intensity")
axs[1].set_ylabel("Pixel Intensity")

if log:
    axs[2].set_ylabel("Pixel Intensity (log scale)")
    axs[2].set_yscale('log')
else:
    axs[2].set_ylabel("Pixel Intensity")

axs[3].set_ylabel("Pixel Intensity")
axs[4].set_ylabel("Pixel Intensity")
axs[4].set_ylim(0, 1)

# GET TICkS
rule = rrulewrapper(MONTHLY, interval=6)
loc = RRuleLocator(rule)
axs[-1].xaxis.set_major_locator(loc)
formatter = DateFormatter('%m/%y')
axs[-1].xaxis.set_major_formatter(formatter)
axs[-1].xaxis.set_tick_params(rotation=30, labelsize=10)
axs[-1].set_xlabel("Date")

for ax in axs[[0, 1, 3]]:
    ax_handles, ax_labels = ax.get_legend_handles_labels()
    handles += ax_handles
    labels += ax_labels

fig.legend(handles, labels, loc='upper right')

# for ax in axs[[0, 1, 3]]:
#     # Put a legend to the right of the current axis
#     box = ax.get_position()
#     ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
if cam:
    fig.savefig(f"percentile_plots/cam_{mode}_normalising_percentiles"
                f"{func}.png",
                bbox_inches='tight')
else:
    fig.savefig(f"percentile_plots/{mode}_normalising_percentiles.png"
                f"{func}",
                bbox_inches='tight')


# normalise data
data = np.sort(os.listdir(np_dir))
data = np.delete(data, outlier_indicies)
data = data[n//2-1:-n//2]

print(len(data), len(rolling_75p))
if get_min_max:
    from scipy.stats import percentileofscore
    minp = []
    maxp = []

    for i in range(len(data) - 1):
        name = data[i]
        max_value = rolling_75p[i]*clip_max
        filename = np_dir + name
        img = np.load(filename).flatten()
        lower_p = percentileofscore(img, 0)
        upper_p = percentileofscore(img, max_value)
        print(f"{name}, lower: {lower_p}, upper: {upper_p}")
        minp.append(lower_p)
        maxp.append(upper_p)

    np.save(f"DATA/np_objects/{mode}_minp", np.array(minp))
    np.save(f"DATA/np_objects/{mode}_maxp", np.array(maxp))


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
