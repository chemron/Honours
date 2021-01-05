import numpy as np
import matplotlib.pyplot as plt
import os
plt.switch_backend("agg")
modes = ["phase_map"]  # , "STEREO", "HMI", "AIA"]
normalised = False

for mode in modes:
    if normalised:
        folder = f"DATA/np_{mode}_normalised/"
    else:
        folder = f"DATA/np_{mode}/"

    filename = folder + os.listdir(folder)[0]

    arr = np.load(filename)
    print(np.max(arr), np.min(arr))

    plt.imsave(f"{mode}_test.png", arr, cmap="gray")
