import numpy as np
import matplotlib.pyplot as plt
import os
plt.switch_backend("agg")
modes = ["S_MAP"]

for mode in modes:
    folder = f"DATA/{mode}/"

    filename = folder + os.listdir(folder)[723]
    arr = np.load(filename)
    arr = np.nan_to_num(arr)
    plt.imsave(f"{mode}_test.png", arr, cmap="gray")
