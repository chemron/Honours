import numpy as np
import matplotlib.pyplot as plt
import os


# combine all stereo data into array: data
folder = "stereo_pos_data/"
data = np.array([], dtype=float).reshape(0, 7)
for fname in np.sort(os.listdir(folder)):
    new_data = np.loadtxt(f"{folder}{fname}", dtype=float)
    data = np.concatenate((data, new_data))

# get transpose of data
data = data.T

# plot data
fig, ax = plt.subplots()

ax.set_xlim(-1.5e8, 1.5e8)
ax.set_ylim(-1.5e8, 1.5e8)
ax.plot(data[-3], data[-2])
plt.show()
