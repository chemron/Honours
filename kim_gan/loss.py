import sys
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')

n = 1000


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


i, d, g, l = np.reshape(sys.argv[1:], (len(sys.argv[1:])//4, 4)).astype(np.float).T
fig, axs = plt.subplots(3, 1, figsize=(25, 5))
axs[0].plot(i[n-1:], moving_average(d, n))
axs[0].set_title("Descriminator Loss")
axs[1].plot(i[n-1:], moving_average(g, n))
axs[1].set_title("Generator Loss")
axs[2].plot(i[n-1:], moving_average(l, n))
axs[2].set_title("Generator absolute difference")
fig.savefig("loss.png", bbox_inches='tight')
