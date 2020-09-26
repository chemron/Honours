import numpy as np
# import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta


# combine all stereo data into array: data
start_date = datetime(2010, 6, 2)

end_date = datetime(2020, 8, 3)


folder = "DATA/stereo_pos_data/"
data = np.array([], dtype=float).reshape(0, 7)
for fname in np.sort(os.listdir(folder)):
    new_data = np.loadtxt(f"{folder}{fname}", dtype=float)
    data = np.concatenate((data, new_data))

"""
year: yyyy
doy: day-of-year (counting from 1)
second: is the second-of-day
flag: 0 if the data are predictive, 1 if the data are definitive
x, y, z: coords
"""
year, doy, second, flag, x, y, z = data.T

# get date time from year, doy, second
year = year.astype(int)
year = np.array([datetime(year=y, month=1, day=1) for y in year])

# put seconds and doys into timedelta object to add on to the year
doy = doy.astype(int)
second = second.astype(int)
dt = np.array((doy, second)).T
dt = np.array([timedelta(days=d.item(), seconds=s.item()) for d, s in dt])

stereo_time = year + dt

# angle between acoustic image and stereo A (radians)
angle = np.arctan2(y, x)

# carrington rotation period (days)
period = 27.2753

# time difference between stereo and accoustic map (farside):
dt = angle * period / (2*np.pi)
# convert to timedelta
dt = np.array([timedelta(days=d) for d in dt])


# equivalent time for phase/accoustic maps
# (so that the active regions are in the same position):
aia_time = stereo_time - dt

date = start_date
dt = timedelta(hours=12)
# index for moving through phase and stereo time arrays
i = 0

f = open("DATA/aia_stereo_times.txt", "w")
while date < end_date:
    while aia_time[i] < date:
        i += 1
    # s_time: stereo time that is best for aia_time
    # j: index of best time ^
    if (aia_time[i] - date) < (date - aia_time[i-1]):
        s_time = stereo_time[i]
        j = i
    else:
        s_time = stereo_time[i-1]
        j = i-1
    if abs(date - aia_time[j]) < timedelta(hours=2):
        f.write(date.strftime("%Y.%m.%d_%H:%M:%S") +
                " " +
                s_time.strftime("%Y.%m.%d_%H:%M:%S") +
                "\n")
    date += dt

# # convert to string:
# phase_time = np.array([time.strftime("%Y.%m.%d_%H:%M:%S")
#                       for time in phase_time])
# stereo_time = np.array([time.strftime("%Y.%m.%d_%H:%M:%S")
#                        for time in stereo_time])


# phase_stereo_times = np.stack((phase_time, stereo_time), axis=1)

# np.savetxt("DATA/phase_stereo_times.txt", phase_stereo_times, fmt='%s')


# plot data
# fig, ax = plt.subplots()

# ax.set_xlim(-1.5e8, 1.5e8)
# ax.set_ylim(-1.5e8, 1.5e8)
# ax.plot(data[-3], data[-2])
# plt.show()
