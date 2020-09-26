#!/usr/bin/env python3
# Python code for retrieving HMI and AIA data
from sunpy.net import Fido, attrs as a

# these are needed to slice the data how I want
from sunpy.net.fido_factory import UnifiedResponse
from sunpy.net.vso.vso import QueryResponse

import astropy.units as u  # for AIA
import os
import argparse
from datetime import datetime, timedelta
import numpy as np

# TODO: do many short queryies rather than one large one
email = 'csmi0005@student.monash.edu'
# can make multiple queries and save the details to files based on the AR and
# retrieve the data later

parser = argparse.ArgumentParser()
parser.add_argument("--path",
                    help="directory to store STEREO data",
                    default='./FITS_DATA/STEREO'
                    )
parser.add_argument("--start",
                    help="start time for STEREO (yyyy-mm-dd hh:mm:ss)",
                    default='2011-01-01 00:00:00')
parser.add_argument("--end",
                    help="end date for STEREO (yyyy-mm-dd hh:mm:ss)",
                    default='2017-01-01 00:00:00')

parser.add_argument("--wavelength",
                    help="wavelength of images in angstroms",
                    type=int,
                    default=304
                    )
parser.add_argument("--times",
                    help="path to times file",
                    default="./DATA/phase_stereo_times.txt"
                    )
args = parser.parse_args()

print(args)
# query duration:
STEREO_start = args.start
STEREO_end = args.end
times = args.times
STEREO_path = args.path
wavelength = args.wavelength*u.AA  # wavelength in angstroms


STEREO_start_date = datetime.fromisoformat(STEREO_start)
STEREO_end_date = datetime.fromisoformat(STEREO_end)
os.makedirs(STEREO_path) if not os.path.exists(STEREO_path) else None

# load phase and stereo times
phase_times, stereo_times = np.loadtxt(times, dtype=str).T

phase_times = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                       for time in phase_times
                        ])


stereo_times = np.array([datetime.strptime(time, "%Y.%m.%d_%H:%M:%S")
                        for time in stereo_times
                         ])

STEREO = True
# index of stereo and phase times
i = 0

step = timedelta(days=20)


while STEREO:
    search_end = STEREO_start_date + step
    if search_end > STEREO_end_date:
        search_end = STEREO_end
        STEREO = False

    search_end_date = search_end.strftime("%Y-%m-%d %H:%M:%S")
    
    print(STEREO_start, search_end_date)
    args = [a.Wavelength(wavelength),
            a.vso.Source('STEREO_A'),
            a.Instrument('EUVI'),
            a.Time(STEREO_start, STEREO_end)]

    print(args)

    res_stereo = Fido.search(*args)

    print(res_stereo)
    # put results into qtable
    table = res_stereo.tables[0]

    # get time string of final end time of results
    if len(table) == 0:
        print("Empty table")
        if STEREO_start_date > STEREO_end_date:
            break
        else:
            STEREO_start_date = search_end_date
            STEREO_start = STEREO_start_date.strftime("%Y-%m-%d %H:%M:%S")
            continue

    # original unified responce object
    UR = res_stereo.get_response(0)
    # blocks (list of the data)
    blocks = UR._data

    # slice list how I need:

    times = np.array([datetime.fromisoformat(time[0])
                     for time in table["Start Time"]])
    # index of table:
    j = 0

    # the indexes of the stereo data to download
    indicies = []
    while j < len(times):
        if times[j] > stereo_times[i]:
            if (times[j] - stereo_times[i]) < timedelta(hours=2):
                indicies += [j]
                j += 1
            i += 1
        else:
            j += 1

    blocks = [blocks[k] for k in indicies]

    # build responce object
    q = QueryResponse(blocks)
    # build unified responce object from sliced query responce
    UR = UnifiedResponse(q)

    # start of next run:
    end = table['End Time'][-1][0]
    STEREO_start_date = datetime.fromisoformat(end) + timedelta(hours=6)
    STEREO_start = STEREO_start_date.strftime("%Y-%m-%d %H:%M:%S")
    # if we get to the end of results:
    if STEREO_start_date >= STEREO_end_date:
        STEREO = False

    # Finally, download the data
    downloaded_files = Fido.fetch(UR, path=STEREO_path)
