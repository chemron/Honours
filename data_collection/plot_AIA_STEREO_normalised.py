import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator)
plt.switch_backend('agg')


def plot_mode(mode, ax):
    percentiles = np.load(f"DATA/np_objects/{mode}_normal_p.npy").T
    datetime_dates = np.load(f"DATA/np_objects/{mode}_normal_d.npy")

    for i in range(len(percentiles)-1, - 1, -1):
        ax.plot_date(datetime_dates, percentiles[i],
                     label=f'${q[i]}$th percentile',
                     markersize=1)
    # ax.set_ylim(0, 1)
    ax.set_title(mode)
    # GET TICkS
    rule = rrulewrapper(MONTHLY, interval=12)
    loc = RRuleLocator(rule)
    ax.xaxis.set_major_locator(loc)
    formatter = DateFormatter('%m/%y')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    ax.set_xlabel("Date")


n = 3
fig, axs = plt.subplots(1, n, sharey=False, figsize=(8*n, 4))
q = [0, 0.01, 0.1, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.9, 99.99, 100]
# plot_AIA(axs[0])
# plot_STEREO(axs[1])
plot_mode('AIA', axs[0])
plot_mode('STEREO', axs[1])
plot_mode('HMI', axs[2])


# Put a legend to the right of the current axis
box = axs[-1].get_position()
axs[-1].set_position([box.x0, box.y0, box.width * 0.8, box.height])
axs[-1].legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
# fig.savefig("percentile_plots/AIA_STEREO_normalised.pdf",
#             bbox_inches='tight')
fig.savefig("percentile_plots/AIA_STEREO_normalised.png",
            bbox_inches='tight')
