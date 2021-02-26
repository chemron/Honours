from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load("DATA/np_objects/phase_map_percentiles.npy").T
dates = np.load("DATA/np_objects/phase_map_dates.npy")
plt_dates = [datetime.strptime(date, "%Y%m%d%H%M%S") for date in dates]

# plot percentiles vs dates
fig, ax = plt.subplots(1, 1, figsize=(12, 8), sharex=True)

for i in range(len(percentiles)-1, - 1, -1):
    ax.plot_date(plt_dates, percentiles[i],
                 label=f'${q[i]}$th percentile',
                 markersize=1)


ax.set_ylabel("Pixel value")


# GET TICkS
rule = rrulewrapper(DAILY, interval=1)
formatter = DateFormatter('%d/%m')
ax.set_xlim(datetime(2018, 3, 20), datetime(2018, 4, 15))


# rule = rrulewrapper(MONTHLY, interval=6)
# formatter = DateFormatter('%m/%y')

loc = RRuleLocator(rule)
ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_tick_params(rotation=30, labelsize=10)
ax.set_xlabel("Date")

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
ax.set_adjustable('box-forced')

plt.tight_layout()
fig.savefig("percentile_plots/phase_percentiles.png", bbox_inches='tight')
