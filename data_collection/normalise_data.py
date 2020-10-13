from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')


np_dir = "DATA/np_AIA_not_normalised"
percentiles = np.load("DATA/percentiles.npy").T
dates = np.load("DATA/dates.npy")
datetime_dates = [datetime.strptime(date, "%Y.%m.%d%H:%M:%S")
                  for date in dates]

# plot percentiles vs dates
fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)


axs[0].plot_date(datetime_dates, percentiles[8],
                 label='75th percentile',
                 markersize=1)

# get cutoff

cutoff = np.array([35 if (x < datetime(2014, 1, 1))
                   else 10 if (x < datetime(2016, 1, 1))
                   else 6 for x in datetime_dates])

axs[0].plot_date(datetime_dates, cutoff,
                 label='Outlier cutoff',
                 markersize=1)

outlier_indicies = np.nonzero(percentiles[8] < cutoff)

percentiles = np.delete(percentiles, outlier_indicies, 1)
dates = np.delete(dates, outlier_indicies)
datetime_dates = np.delete(datetime_dates, outlier_indicies)


# moving average over 50 images
n = 50


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


rolling_75p = moving_average(percentiles[8], n)
rolling_dates = dates[n//2-1:-n//2]
percentiles = percentiles.T[n//2-1:-n//2].T
datetime_dates = datetime_dates[n//2-1:-n//2]

normal_percentiles = percentiles/rolling_75p

axs[1].plot_date(datetime_dates, rolling_75p,
                 label=f'Rolling 75th percentile\n(over {n} images)',
                 markersize=1)


q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
for i in range(len(percentiles)-1, len(percentiles)//2 - 1, -1):
    axs[2].plot_date(datetime_dates, normal_percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)

normal_percentiles[-1] = np.clip(normal_percentiles[-1],
                                 None,
                                 np.max(normal_percentiles[-1][:60]))
for i in range(len(percentiles)-1, len(percentiles)//2 - 1, -1):
    axs[3].plot_date(datetime_dates, normal_percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)

axs[0].set_ylabel("Pixel Intensity")
axs[1].set_ylabel("Pixel Intensity")
axs[2].set_ylabel("Pixel Intensity (log scale)")
axs[3].set_ylabel("Pixel Intensity (log scale)")
axs[2].set_yscale('log')
axs[3].set_yscale('log')

# GET TICkS
rule = rrulewrapper(MONTHLY, interval=6)
loc = RRuleLocator(rule)
axs[2].xaxis.set_major_locator(loc)
formatter = DateFormatter('%m/%y')
axs[2].xaxis.set_major_formatter(formatter)
axs[2].xaxis.set_tick_params(rotation=30, labelsize=10)
axs[2].set_xlabel("Date")

for ax in axs:
    # Put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_adjustable('box-forced')

plt.tight_layout()
fig.savefig("normalising_percentiles.png", bbox_inches='tight')
