import sys
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')

n = 10000


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


data = np.loadtxt(sys.argv[1]).T
titles = ["Descriminator Loss",
          "Generator Loss",
          "Generator Absolute Difference"
          ]
fig, axs = plt.subplots(3, 1, figsize=(25, 10))
for i in range(3):
    axs[i].plot(data[0][n-1:], moving_average(data[i+1], n))
    axs[i].set_title(titles[i])
fig.savefig("loss.png", bbox_inches='tight')
