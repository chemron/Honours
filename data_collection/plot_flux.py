import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator)
# plt.switch_backend('agg')

n = 5000


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

dates = []
fluxes = []
data = open(sys.argv[1], "r")
for line in data:
    date, flux = line.split()
    date = datetime.strptime(date[:-3], "%Y-%m-%dT%H:%M:%S")
    flux = float(flux)
    if flux >= 1e20:
        continue
    dates.append(date)
    fluxes.append(flux)
data.close

x_flares = open("DATA/unsigned_flux/x_flare_list.txt", "r")
x_dates = []
for line in x_flares:
    y, m, d = line.split("/")
    y = int(y)
    m = int(m)
    d = int(d[:-1])
    x_dates.append(datetime(year=y, month=m, day=d))
data.close


plt.figure(1, figsize=(25, 10))
ax = plt.subplot(1, 1, 1)
# rule = rrulewrapper(MONTHLY, interval=6)
# loc = RRuleLocator(rule)
# ax.xaxis.set_major_locator(loc)
formatter = DateFormatter('%d/%m/%y')
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_tick_params(rotation=30, labelsize=10)
ax.set_xlabel("Date")
ax.set_ylabel("Flux")
for x_date in x_dates:
    ax.axvline(x_date, c='r')

plt.plot(dates, fluxes, c='k')
# plt.show()
plt.savefig("Flux_vs_time.png")
