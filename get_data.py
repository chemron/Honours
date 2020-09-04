#!/usr/bin/env python3
# Python code for retrieving HMI and AIA data
from sunpy.net import Fido, attrs as a

from datetime import datetime, timedelta
import astropy.units as u  # for AIA
import argparse
import numpy as np

import drms
import time
from sunpy.util.parfive_helpers import Downloader

from urllib.error import HTTPError

email = 'camerontasmith@gmail.com'

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
    # start time for downloading
    s_time = datetime.fromisoformat(start)
    # time of end of downloading
    f_time = datetime.fromisoformat(end)
    # take data from 30 days at a time
    step_time = timedelta(days=30)
    # time of end of this step:
    e_time = s_time + step_time
    # time between searches
    cadence = timedelta(hours=cadence)
    path = f"{path}fits_{name}/"

    while True:
        if e_time > f_time:
            e_time = f_time

        start = s_time.strftime("%Y-%m-%d %H:%M:%S")
        end = e_time.strftime("%Y-%m-%d %H:%M:%S")
        args = [a.Time(start, end),
                a.jsoc.Notify(email),
                a.jsoc.Series(series),
                a.jsoc.Segment(segment),
                a.Sample(0.3*u.hour)
                ]

        if wavelength != 0:
            args.append(a.jsoc.Wavelength(wavelength))

        res = Fido.search(*args)

        # get response object:
        table = res.tables[0]

        # get time string of final end time of results
        if len(table) == 0:
            print(f"{s_time} to {e_time}: Empty table")
            if e_time >= f_time:
                print("finish on empty table")
                return
            else:
                s_time = e_time
                e_time += step_time
                continue

        # get times:
        times = np.array([datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
                          for time in table["T_REC"]])

        index, dates = get_index(times, s_time, e_time, cadence)

        print(index)

        request = get_request(res, index)

        urls = request.urls.url[index]

        downloader = Downloader(progress=True, overwrite=False, max_conn=4)

        for url, date in zip(urls, dates):
            filename = f"{path}{name}_{date.year}.{date.month:0>2}." \
                       f"{date.day:0>2}_{date.hour:0>2}:00:00.fits"
            print(filename)
            downloader.enqueue_file(url, filename=filename, max_splits=2)

        downloader.download()

        # start of next run:
        if e_time >= f_time:
            return

        s_time = e_time
        e_time += step_time


def get_index(times, start: datetime, end: datetime, cadence: timedelta):
    # get index and dates of every cadence timestep in times
    index = []
    dates = []
    # current time:
    current = start

    i = 0
    while i < len(times):
        # previous time in times
        p_time = times[i-1]
        # current time in times
        time = times[i]
        if time > current:
            # if the previous time was closer to current:
            if (current - p_time) < (time - current):
                time = p_time
                i = i - 1
            # add the time to the index if close enough
            if (time - current) < timedelta(hours=2):
                index.append(i)
                dates.append(time)
            current += cadence
        i += 1

    return index, dates


def get_request(res, index):
    # get response
    jsoc_response = list(res.responses)[0]
    # get block (info about response)
    block = jsoc_response.query_args[0]
    # data string
    ds = jsoc_response.client._make_recordset(**block)
    # client for drms
    cd = drms.Client(email=block.get('notify', ''))
    request = cd.export(ds, method='url', protocol='fits')

    print("waiting for request", end="")
    while request.status == 0:
        print(".", end="")
        time.sleep(5)

    print("\ndone")

    return request


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
