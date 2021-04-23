import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DAILY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')


folder = "DATA/unsigned_flux/"
# plot with line plot
modes_line = ["hmi", "gan_ste_full"]
n_l = len(modes_line)
# plot with scatter plot
modes_scatter = ["gan_16_kernal_size_test", "gan_16_kernal_size_train", "gan_batch", "gan_low_tol"]
n_s = len(modes_scatter)
flares = False
average = True


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def get_data(mode):
    dates = []
    fluxes = []
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
    
    if average:    
        n = 55
        fluxes = moving_average(fluxes, n)
        dates = dates[n//2:-n//2 + 1]
    data.close()
    return dates, fluxes


def plot_flares(ax):
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



# set up figure
plt.figure(1, figsize=(15, 8))
ax = plt.subplot(1, 1, 1)
# rule = rrulewrapper(MONTHLY, interval=6)
# loc = RRuleLocator(rule)
# ax.xaxis.set_major_locator(loc)
formatter = DateFormatter('%d/%m/%y')
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_tick_params(rotation=30, labelsize=10)
ax.set_xlabel("Date (day/month/year)")
ax.set_ylabel("Flux")
# ax.set_ylim(1e18, 1e21)
# colours
cmap = list(plt.get_cmap("tab10").colors)
c = 0


if flares:
    plot_flares(ax)


# plot actual flux
for mode in modes_line:
    data = get_data(mode)
    plt.plot(*data, label=f"Flux according to {mode.upper()}", c=cmap[c])
    c += 1


# plot for gans flux's
for mode in modes_scatter:
    data = get_data(mode)
    plt.scatter(*data, label=f"Flux according to {mode}", c=cmap[c], s=4)
    c += 1

title_str = "Total Unsigned Magnetic Flux vs Time"
if average:
    title_str += " with ~27 day rolling average"
plt.title(title_str)
plt.tight_layout
plt.legend()
plt.savefig("Flux_vs_time.png")
