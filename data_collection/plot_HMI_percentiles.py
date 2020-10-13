from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load("DATA/HMI_percentiles.npy")
dates = np.load("DATA/HMI_dates.npy")
plt_dates = np.array([datetime.strptime(date, "%Y%m%d%H%M%S")
                      for date in dates])

# crop between start and end
start = datetime(2014, 1, 1)
end = datetime(2014, 2, 1)

start_i = np.argmax(plt_dates > start)
end_i = np.argmax(plt_dates > end)
plt_dates = plt_dates[start_i:end_i]
percentiles = percentiles[start_i:end_i]


# plot percentiles vs dates
percentiles = percentiles.T
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

for i in range(len(percentiles)-1, - 1, -1):
    axs[0].plot_date(plt_dates, percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)
for i in range(len(percentiles)-1, 7, -1):
    axs[1].plot_date(plt_dates, np.abs(percentiles[i]),
                     label=f'${q[i]}$th percentile',
                     markersize=1)

axs[0].set_ylabel("Pixel value")
axs[1].set_ylabel("Absolute pixel value (log scale)")
axs[1].set_yscale('log')


# GET TICkS
# rule = rrulewrapper(MONTHLY, interval=6)
rule = rrulewrapper(DAILY)
loc = RRuleLocator(rule)
axs[1].xaxis.set_major_locator(loc)
formatter = DateFormatter('%d/%m/%y')
axs[1].xaxis.set_major_formatter(formatter)
axs[1].xaxis.set_tick_params(rotation=30, labelsize=10)
axs[1].set_xlabel("Date")
for ax in axs:
    # Put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_adjustable('box-forced')

plt.tight_layout()
fig.savefig("HMI_percentiles_crop.png", bbox_inches='tight')
