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
                    default='HMI'
                    )
parser.add_argument("--just_plot",
                    action="store_true",
                    )
args = parser.parse_args()
mode = args.data


np_dir = f"DATA/np_{mode}/"
normal_np_dir = f"DATA/np_{mode}_normalised/"
os.makedirs(normal_np_dir) if not os.path.exists(normal_np_dir) else None

percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
dates = np.load(f"DATA/np_objects/{mode}_dates.npy")
datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                  for date in dates]
# don't normalise data, just plot percentiles:
just_plot = args.just_plot
w = h = 1024  # desired width and height of output
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]

# plot percentiles vs dates
fig, axs = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

for i in range(len(percentiles)-1, - 1, -1):
    axs[0].plot_date(datetime_dates, percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)


abs_max = abs(np.max(percentiles[-1]))
abs_min = abs(np.min(percentiles[0]))

print(f"Absolute max: {abs_max}, Absolute min: {abs_min}")

clip_max = np.max([abs_max, -abs_min])

clipped_percentiles = percentiles.clip(-clip_max, clip_max)
clipped_percentiles = clipped_percentiles/clip_max

for i in range(len(percentiles)-1, - 1, -1):
    axs[1].plot_date(datetime_dates, clipped_percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)

axs[0].set_ylabel("Magnetic field strength (Gauss)")
axs[1].set_ylabel("Normalised magnetic field strength")

# GET TICkS
rule = rrulewrapper(MONTHLY, interval=6)
loc = RRuleLocator(rule)
axs[1].xaxis.set_major_locator(loc)
formatter = DateFormatter('%m/%y')
axs[1].xaxis.set_major_formatter(formatter)
axs[1].xaxis.set_tick_params(rotation=30, labelsize=10)
axs[1].set_xlabel("Date")

for ax in axs:
    # Put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
fig.savefig(f"percentile_plots/{mode}_normalising_percentiles.png",
            bbox_inches='tight')

# normalise data
data = np.sort(os.listdir(np_dir))

if not just_plot:
    import cv2
    for i in range(len(data)):
        name = data[i]
        filename = np_dir + name
        img = np.load(filename)
        img = img/clip_max
        img = img.clip(-1, 1)
        try:
            img = cv2.resize(img, dsize=(w, h))
            np.save(normal_np_dir + name, img)
        except cv2.error as e:
            print(f"{name}: {e}")
