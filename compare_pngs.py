import os
import numpy as np
from datetime import datetime, timedelta
from PIL import Image


png_path_1 = "DATA/png_aia/"
png_path_2 = "DATA/png_stereo_aia/"
time_path = "DATA/aia_stereo_times.txt"
combined_path = "DATA/png_stereo_aia_combined/"

os.makedirs(combined_path) if not os.path.exists(combined_path) else None

pngs_1 = np.sort(os.listdir(png_path_1))
pngs_2 = np.sort(os.listdir(png_path_2))


def join_images(png_1, png_2, filename):
    images = [Image.open(x) for x in [png_1, png_2]]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(filename)


# get times from text file
times_1, times_2 = np.loadtxt(time_path, dtype=str).T

times_1 = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                    for time in times_1
                    ])

times_2 = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                    for time in times_2
                    ])

# get times of pngs
png_times_1 = np.array([datetime.strptime(f, "AIA_%Y.%m.%d_%H:%M:%S.png")
                        for f in pngs_1])
png_times_2 = np.array([datetime.strptime(f[:26], "STEREO_%Y.%m.%d_%H:%M:%S")
                        for f in pngs_2])

time_index = 0
png_index_1 = 0
png_index_2 = 0

while time_index < len(times_1):
    # get index for png_times_1
    while times_1[time_index] > png_times_1[png_index_1] and \
          png_index_1 < len(pngs_1) - 1:
        png_index_1 += 1
    if abs(png_times_1[png_index_1] - times_1[time_index]) > \
       abs(png_times_1[png_index_1 - 1] - times_1[time_index]):
        png_index_1 = png_index_1 - 1

    # get index for png_times_2
    while times_2[time_index] > png_times_2[png_index_2] and \
          png_index_2 < len(pngs_2) - 1:
        png_index_2 += 1
    if abs(png_times_2[png_index_2] - times_2[time_index]) > \
       abs(png_times_2[png_index_2 - 1] - times_2[time_index]):
        png_index_2 = png_index_2 - 1

    if (abs(png_times_1[png_index_1] - times_1[time_index]) <
       timedelta(hours=2)) and \
       (abs(png_times_2[png_index_2] - times_2[time_index]) <
       timedelta(hours=2)):
        time_1 = png_times_1[png_index_1].strftime("%Y.%m.%d")
        time_2 = png_times_2[png_index_2].strftime("%Y.%m.%d")

        filename = f"{combined_path}aia_stereo_{time_1}_{time_2}.png"
        join_images(f"{png_path_1}{pngs_1[png_index_1]}",
                    f"{png_path_2}{pngs_2[png_index_2]}",
                    filename)

    time_index += 1
