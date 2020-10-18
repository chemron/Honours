import numpy as np
import matplotlib.pyplot as plt
import os

plt.switch_backend("agg")

folder = "DATA/np_HMI_normalised/"
filename = folder + os.listdir(folder)[0]

arr = np.load(filename)
print(np.max(arr), np.min(arr))

plt.imsave("HMI_test.png", arr)

