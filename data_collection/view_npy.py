import numpy as np
import matplotlib.pyplot as plt
import os

plt.switch_backend("agg")

folder = "DATA/np_HMI/"
filename = folder + os.listdir(folder)[0]

arr = np.load(filename)

plt.imsave("HMI_test.png", arr)

