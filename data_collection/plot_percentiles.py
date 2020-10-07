from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator
plt.switch_backend('agg')

q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
percentiles = np.load("DATA/percentiles.npy")
dates = np.load("DATA/dates.npy")
plt_dates = [datetime.strptime(date, "%Y.%m.%d%H:%M:%S") for date in dates]

fig, ax = plt.subplots(figsize=(35, 10))
for i in range(len(percentiles)):
    ax.plot_date(plt_dates, percentiles[i], label=f'${q[i]}$th percentile')
ax.set_yscale('log')
ax.set_ylabel("Pixel Intensity (log scale)")
ax.set_xlabel("Date")
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.xaxis.set_major_locator(MonthLocator())
# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
fig.savefig("percentiles.png")
