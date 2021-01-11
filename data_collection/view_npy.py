import numpy as np
import matplotlib.pyplot as plt
import os
plt.switch_backend("agg")
modes = ["phase_map"]  # ["phase_map", "STEREO", "HMI", "AIA"]
normalised = False

for mode in modes:
    if normalised:
        folder = f"DATA/np_{mode}_normalised/"
    else:
        folder = f"DATA/np_{mode}/"

    filename = folder + np.sort(os.listdir(folder))[0]
    # filename = folder + "STE_2012.05.20_01:46:15.npy" "PHASE_MAP_2012.05.25_00:00:00.npy" 

    arr = np.load(filename)
    arr = np.nan_to_num(arr)
    print(np.max(arr), np.min(arr))

    plt.imsave(f"{mode}_test.png", arr, cmap="gray")
