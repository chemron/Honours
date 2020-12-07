from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')

mode = 'STEREO'
func = ''
log = False

# moving average over 50 images
n = 50

percentiles = np.load(f"DATA/np_objects/{mode}_percentiles.npy").T
dates = np.load(f"DATA/np_objects/{mode}_dates.npy")
if mode == "STEREO":
    dates = np.apply_along_axis(lambda d: d[0] + d[1], 1, dates)

datetime_dates = [datetime.strptime(date, "%Y%m%d%H%M%S")
                  for date in dates]
# don't normalise data, just plot percentiles:

n_ax = 6
current_ax = 0
# plot percentiles vs dates
fig, axs = plt.subplots(n_ax, 1, figsize=(10, n_ax*2.5), sharex=True)
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
handles = []
labels = []

# get colors:
cmap = list(plt.get_cmap("tab10").colors)
cmap = cmap + cmap
cmap = cmap[14::-1]
# switch so green is 75th percentile
green = cmap[-3]
cmap = cmap[:8] + [green] + cmap[8:-3] + cmap[-2:]

# raw percentiles

for i in range(len(percentiles)-1, -1, -1):
    axs[current_ax].plot_date(datetime_dates, percentiles[i],
                              label=f'${q[i]}$th percentile',
                              c=cmap[i],
                              markersize=1)

# axs[current_ax].set_yscale('log')
axs[current_ax].set_ylim(500, 17500)
axs[current_ax].set_ylabel("Raw Pixel Intensity\n Percentiles")
# next ax:
ax_handles, ax_labels = axs[current_ax].get_legend_handles_labels()
handles += ax_handles
labels += ax_labels
current_ax += 1

# zero point
zero_point = np.load("DATA/np_objects/STEREO_zeros.npy")
zero_point = np.average(zero_point)
zero_point = int(np.round(zero_point))

percentiles -= zero_point
print(f'Zero point is: {zero_point}')


# shifted percentiles

for i in range(len(percentiles)-1, -1, -1):
    axs[current_ax].plot_date(datetime_dates, percentiles[i],
                              label=f'${q[i]}$th percentile',
                              c=cmap[i],
                              markersize=1)

# axs[current_ax].set_yscale('log')
axs[current_ax].set_ylim(500 - zero_point, 17500 - zero_point)
axs[current_ax].set_ylabel("Shifted Pixel\n Intensity Percentiles")
# ax_handles, ax_labels = axs[current_ax].get_legend_handles_labels()
# handles += ax_handles
# labels += ax_labels
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
                          label='Outlier cutoff',
                          linestyle="-",
                          marker="",
                          c="k")


axs[current_ax].plot_date(datetime_dates, lower_cutoff,
                          linestyle="-",
                          marker="",
                          c="k")


axs[current_ax].plot_date(datetime_dates, percentiles[8],
                          markersize=1,
                          c=green)

axs[current_ax].set_ylim(900 - zero_point, 1400 - zero_point)
axs[current_ax].set_ylabel("75th Percentile\n Pixel Intensity")
ax_handles, ax_labels = axs[current_ax].get_legend_handles_labels()
handles += ax_handles
labels += ax_labels
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
axs[current_ax].plot_date(datetime_dates, rolling_75p,
                          label=f'Rolling 75th percentile\n(over {n} images)',
                          markersize=1,
                          c=green)
axs[current_ax].set_ylim(900 - zero_point, 1400 - zero_point)
axs[current_ax].set_ylabel("Rolling 75th\n Percentile Pixel\n Intensity")
ax_handles, ax_labels = axs[current_ax].get_legend_handles_labels()
handles += ax_handles
labels += ax_labels
current_ax += 1


# # clip max from AIA
# clip_max = 110.59708760329583
# normal_percentiles = normal_percentiles/clip_max

# normal percentiles
normal_percentiles = percentiles/rolling_75p


# rolling max:
# generate next list from which to take max from:
def gen_rolling_list(lst, k):
    n = len(lst)
    current_lst = lst[:k]
    for i in range(n):
        if (i > k) and (i < n-k):
            right = min(i + k//2, n)
            left = max(0, right - k)
            current_lst = lst[left:right]

        yield max(current_lst)


rolling_max = list(gen_rolling_list(normal_percentiles[-1], 50))
clip_max = min(rolling_max)


# axs[current_ax].plot_date(datetime_dates, rolling_max,
#                           label='rolling max',
#                           markersize=1)
# axs[current_ax].set_ylim(0)
# axs[current_ax].set_ylabel("Rolling max")
# handles += ax_handles
# labels += ax_labels
# current_ax += 1

for i in range(len(percentiles)-1, -1, -1):
    axs[current_ax].plot_date(datetime_dates, normal_percentiles[i],
                              # label=f'${q[i]}$th percentile',
                              c=cmap[i],
                              markersize=1)


# plot clip max
clip_max_line = np.full(len(normal_percentiles[-1]), clip_max)
axs[current_ax].plot_date(datetime_dates, clip_max_line,
                          label='Clip point',
                          linestyle="--",
                          marker="",
                          c='k')
ax_handles, ax_labels = axs[current_ax].get_legend_handles_labels()
handles += ax_handles
labels += ax_labels
axs[current_ax].set_ylim(0)
axs[current_ax].set_ylabel("Normalised Pixel\n Intensity Percentiles")
current_ax += 1

# scale so min max is 1
print(f"Clip max is: {clip_max}")
normal_percentiles = normal_percentiles/clip_max


# transform data
normal_percentiles = np.sign(normal_percentiles) * \
                      (np.abs(normal_percentiles)**(1/2))


for i in range(len(percentiles)-1, -1, -1):
    axs[current_ax].plot_date(datetime_dates, normal_percentiles[i],
                              #  label=f'${q[i]}$th percentile',
                              c=cmap[i],
                              markersize=1)


axs[current_ax].set_ylabel("Pixel Intensity")
axs[current_ax].set_ylabel("Pixel Intensity")

if log:
    axs[current_ax].set_ylabel("Pixel Intensity (log scale)")
    axs[current_ax].set_yscale('log')
else:
    axs[current_ax].set_ylabel("Pixel Intensity")

axs[current_ax].set_ylabel("Pixel Intensity")
axs[current_ax].set_ylabel("Pixel Intensity")
axs[current_ax].set_ylim(0, 1)

# GET TICkS
rule = rrulewrapper(MONTHLY, interval=6)
loc = RRuleLocator(rule)
axs[-1].xaxis.set_major_locator(loc)
formatter = DateFormatter('%m/%y')
axs[-1].xaxis.set_major_formatter(formatter)
axs[-1].xaxis.set_tick_params(rotation=30, labelsize=10)
axs[-1].set_xlabel("Date")
axs[-1].set_xlim(datetime_dates[0], datetime_dates[-1])

# ax_handles, ax_labels = axs[current_ax].get_legend_handles_labels()
# handles += ax_handles
# labels += ax_labels

fig.legend(handles, labels, loc='upper right')

# for ax in axs[[0, 2, 3]]:
#     # Put a legend to the right of the current axis
#     box = ax.get_position()
#     ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
#     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()

fig.savefig(f"percentile_plots/{mode}_normalising_percentiles.png"
            f"{func}",
            bbox_inches='tight')
