from bisect import bisect_left
import numpy as np

phase_times, stereo_times = np.load("./DATA/phase_stereo_times.npy",
                                    allow_pickle=True).T


def get_stereo_time(phase_time):
    pos = bisect_left(phase_times, phase_time)
    if pos == 0:
        return stereo_times[0]
    if pos == len(phase_times):
        return stereo_times[-1]
    before = phase_times[pos - 1]
    after = phase_times[pos]
    if abs(after - phase_time) < abs(phase_time - before):
        return stereo_times[pos]
    else:
        return stereo_times[pos-1]
