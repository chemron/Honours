import numpy as np
import matplotlib.pyplot as plt
import os

plt.switch_backend("agg")
modes = ["HMI", "AIA"]
for mode in modes:
    folder = f"DATA/np_{mode}_normalised_sqrt/"
    filename = folder + os.listdir(folder)[0]

    arr = np.load(filename)
    print(np.max(arr), np.min(arr))

    plt.imsave(f"{mode}_test.png", arr, cmap="gray")
