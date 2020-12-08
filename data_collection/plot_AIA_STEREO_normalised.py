from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def plot_AIA(ax):
    # moving average over 50 images
    mode = "AIA"
    n = 50

    percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
    dates = np.load(f"DATA/np_objects/{mode}_dates.npy")

    datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                      for date in dates]

    cutoff = np.array([45 if (x < datetime(2014, 1, 1))
                      else 20 if (x < datetime(2015, 2, 1))
                      else 8 for x in datetime_dates])

    outlier_indicies = np.nonzero(percentiles[8] < cutoff)

    percentiles = np.delete(percentiles, outlier_indicies, 1)
    dates = np.delete(dates, outlier_indicies)
    datetime_dates = np.delete(datetime_dates, outlier_indicies)

    rolling_75p = moving_average(percentiles[8], n)
    percentiles = percentiles.T[n//2-1:-n//2].T
    datetime_dates = datetime_dates[n//2-1:-n//2]
    normal_percentiles = percentiles/rolling_75p
    clip_max = np.max(normal_percentiles[-1][:50])

    normal_percentiles = normal_percentiles.clip(None, clip_max)

    normal_percentiles = normal_percentiles/clip_max

    for i in range(len(percentiles)-1, - 1, -1):
        ax.plot_date(datetime_dates, normal_percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)

    # GET TICkS
    rule = rrulewrapper(MONTHLY, interval=6)
    loc = RRuleLocator(rule)
    ax.xaxis.set_major_locator(loc)
    ax.set_ylim(0, 1)
    ax.set_title("AIA")
    formatter = DateFormatter('%m/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Pixel Intensity (normalised)")


def plot_STEREO(ax):
    mode = "STEREO"

    percentiles = np.load(f"DATA/np_objects/{mode}_normal_p.npy").T
    datetime_dates = np.load(f"DATA/np_objects/{mode}_normal_d.npy")

    for i in range(len(percentiles)-1, - 1, -1):
        ax.plot_date(datetime_dates, percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)
    ax.set_ylim(0, 1)
    ax.set_title("STEREO")
    # GET TICkS
    rule = rrulewrapper(MONTHLY, interval=6)
    loc = RRuleLocator(rule)
    ax.xaxis.set_major_locator(loc)
    formatter = DateFormatter('%m/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    ax.set_xlabel("Date")


fig, axs = plt.subplots(1, 2, sharey=True, figsize=(15, 4))
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
plot_AIA(axs[0])
plot_STEREO(axs[1])

# Put a legend to the right of the current axis
box = axs[1].get_position()
axs[1].set_position([box.x0, box.y0, box.width * 0.8, box.height])
axs[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
# fig.savefig("percentile_plots/AIA_STEREO_normalised.pdf",
#             bbox_inches='tight')
fig.savefig("percentile_plots/AIA_STEREO_normalised.png",
            bbox_inches='tight')
