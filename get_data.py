#!/usr/bin/env python3
# Python code for retrieving HMI and AIA data
from sunpy.net import Fido, attrs as a

from datetime import datetime, timedelta
import astropy.units as u  # for AIA
import argparse
import numpy as np

from urllib.error import HTTPError

email = 'csmi0005@student.monash.edu'

# can make multiple queries and save the details to files based on the AR and
# retrieve the data later


parser = argparse.ArgumentParser()
parser.add_argument("--instruments",
                    nargs="+",
                    help="<required> download data from these instruments",
                    required=True
                    )
parser.add_argument("--series",
                    nargs="+",
                    help="series for each instrument in --Instrument list",
                    default=['aia.lev1_euv_12s', 'hmi.m_45s'])
parser.add_argument("--segment",
                    nargs="+",
                    help="segments for each instrument in --Instrument list."
                         " Use \"None\" for None",
                    default=['image', "magnetogram"])
parser.add_argument("--start",
                    help="start date for AIA and HMI",
                    default='2010-06-01 00:00:00')
parser.add_argument("--end",
                    help="end date for AIA and HMI",
                    default='2020-01-01 00:00:00')
parser.add_argument("--cadence",
                    help="AIA and HMI cadence in hours",
                    type=int,
                    default=12
                    )
parser.add_argument("--path",
                    help="directory to store data",
                    default='./DATA/'
                    )
parser.add_argument("--wavelength",
                    help="wavelength of images in angstroms"
                         " Use 0 for None",
                    nargs="+",
                    type=int,
                    default=[304, 0]
                    )
args = parser.parse_args()


def get_data(name: str, series: str, segment: str, start: str, end: str,
             cadence: int, wavelength: int, path: str):

    wavelength = wavelength*u.AA
    # current time of downloading

    c_time = datetime.fromisoformat(start)
    # time of end of downloading
    f_time = datetime.fromisoformat(end)
    cadence = cadence*u.hour
    # take data from 30 days at a time
    step_time = timedelta(days=30)
    # time of end of this step:
    e_time = c_time + step_time
    # time of start of this step
    s_time = e_time

    path = f"{path}fits_{name}"

    while True:

        start = s_time.strftime("%Y-%m-%d %H:%M:%S")
        end = e_time.strftime("%Y-%m-%d %H:%M:%S")
        args = [a.Time(start, end),
                a.jsoc.Notify(email),
                a.jsoc.Series(series),
                a.jsoc.Segment(segment),
                a.Sample(1*u.hour)
                ]

        if wavelength != 0:
            args.append(a.jsoc.Wavelength(wavelength))

        res = Fido.search(*args)

        print(res)

        # get response object:
        table = res.tables[0]

        # get time string of final end time of results
        if len(table) == 0:
            print(f"{c_time} to {e_time}: Empty table")
            if e_time >= c_time:
                print("finish on empty table")
                return
            else:
                s_time = c_time = e_time
                e_time += step_time
                continue


        # slice list how I need:

        # get times:
        times = np.array([datetime.fromisoformat(time[0])
                          for time in table["Start Time"]])
        # index of table:
        j = 0
     # Finally, download the data
        files = Fido.fetch(UR, path=path)

        # start of next run:
        if c_time >= f_time:
            return

        s_time = c_time = e_time
        e_time += step_time


# number of instruments
n = len(args.instruments)

for i in range(n):
    try:
        print(args.instruments[i],
              args.segment[i],
              args.series[i],
              args.start,
              args.end,
              args.cadence,
              args.wavelength[i],
              args.path)
        get_data(name=args.instruments[i],
                 segment=args.segment[i],
                 series=args.series[i],
                 start=args.start,
                 end=args.end,
                 cadence=args.cadence,
                 wavelength=args.wavelength[i],
                 path=args.path)
    except HTTPError as e:
        print(e)
        pass
