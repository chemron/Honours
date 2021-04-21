import numpy as np
import matplotlib.pyplot as plt
import os
plt.switch_backend("agg")
modes = ["np_phase_map_square"]

for mode in modes:
    folder = f"DATA/{mode}/"

    filename = folder + np.sort(os.listdir(folder))[0]
    arr = np.load(filename)
    arr = np.nan_to_num(arr)
    plt.imsave(f"{mode}_test.png", arr, cmap="gray")
