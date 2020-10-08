from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load("DATA/percentiles.npy").T
dates = np.load("DATA/dates.npy")
plt_dates = [datetime.strptime(date, "%Y.%m.%d%H:%M:%S") for date in dates]

# plot percentiles vs dates
fig, axs = plt.subplots(2, 1, figsize=(15, 10))
for i in range(len(percentiles)-1, len(percentiles)//2 - 1, -1):
    axs[0].plot_date(plt_dates, percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)
for i in range(len(percentiles)//2 - 1, -1, -1):
    axs[1].plot_date(plt_dates, percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=2)

axs[0].set_yscale('log')

for ax in axs:
    # labels
    ax.set_ylabel("Pixel Intensity (log scale)")
    ax.set_xlabel("Date")

    # Put a legend to the right of the current axis
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # GET TICkS
    rule = rrulewrapper(MONTHLY, interval=6)
    loc = RRuleLocator(rule)
    ax.xaxis.set_major_locator(loc)
    formatter = DateFormatter('%m/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)

fig.savefig("percentiles.png", bbox_inches='tight')
