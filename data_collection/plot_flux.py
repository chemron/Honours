import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')

def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

folder = "DATA/unsigned_flux/"
modes = ["gan_batch", "gan_default", "gan_low_tol", "gan_ste"]
n_m = len(modes)


# set up figure
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
# ax.set_ylim(1e18, 1e21)
# colours
cmap = list(plt.get_cmap("tab10").colors)

# plot flares
x_flares = open(f"{folder}x_flare_list.txt", "r")
x_dates = []
for line in x_flares:
    y, m, d = line.split("/")
    y = int(y)
    m = int(m)
    d = int(d[:-1])
    x_dates.append(datetime(year=y, month=m, day=d))
x_flares.close
n_x = len(x_dates)


for i in range(n_x):
    x_date = x_dates[i]
    ax.axvline(x_date, c='r', label="x class flare" if i==0 else "")

# plot actual flux
mode = 'hmi'
data = open(f"{folder}unsigned_flux_{mode}.txt")
dates = []
fluxes = []
for line in data:
    date, flux = line.split()
    # remove milliseconds
    date = date.split(".")[0]
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    flux = float(flux)
    if flux >= 1e20:
        continue
    dates.append(date)
    fluxes.append(flux)
plt.plot(dates, fluxes, label=f"Flux according to {mode.upper()}", c='k')
# clear variables
dates = []
fluxes = []
data.close

# plot for gans flux's
dates = []
fluxes = []
for i in range(n_m):
    mode = modes[i]
    data = open(f"{folder}unsigned_flux_{mode}.txt")
    for line in data:
        date, flux = line.split()
        # remove milliseconds
        date = date.split(".")[0]
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
        flux = float(flux)
        if flux >= 1e20:
            continue
        dates.append(date)
        fluxes.append(flux)
    plt.scatter(dates, fluxes, label=f"Flux according to {mode}", s=4)
    # clear variables
    dates = []
    fluxes = []
    data.close


plt.legend()
plt.savefig("Flux_vs_time.png")
