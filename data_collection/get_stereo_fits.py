from sunpy.net import Fido, attrs as a

from datetime import datetime, timedelta
import astropy.units as u  # for AIA
import argparse
import numpy as np
import os

from sunpy.net.fido_factory import UnifiedResponse
from sunpy.net.vso.vso import QueryResponse

parser = argparse.ArgumentParser()
parser.add_argument("--start",
                    help="start date",
                    default='2010-06-01 00:00:00')
parser.add_argument("--end",
                    help="end date",
                    default='2020-01-01 00:00:00')
parser.add_argument("--cadence",
                    type=int,
                    default=12
                    )
parser.add_argument("--path",
                    help="directory to store data",
                    default='./DATA/'
                    )
parser.add_argument("--email",
                    default="csmi0005@student.monash.edu")
args = parser.parse_args()

start = args.start
end = args.end
cadence = args.cadence
email = args.email

wavelength = 304*u.AA
source = 'STEREO_A'
instrument = 'EUVI'
path = f"{args.path}fits_STEREO/"
os.makedirs(path) if not os.path.exists(path) else None
cadence = timedelta(hours=cadence)
fmt = "%Y-%m-%d %H:%M:%S"

# start time for downloading
s_time = datetime.fromisoformat(start)
# time of end of downloading
f_time = datetime.fromisoformat(end)
# take data from 10 days at a time
step_time = timedelta(days=8)
# time of end of this step:
e_time = s_time + step_time
# time between searches


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
            if abs(current - p_time) < abs(current - time):
                time = p_time
                i = i - 1
            # add the time to the index if close enough
            if (time - current) < timedelta(hours=2):
                index.append(i)
                dates.append(time)
            current += cadence
        i += 1

    return index, dates


while True:
    if e_time > f_time:
        e_time = f_time
    
    print(f"getting data between {s_time} and {e_time}")

    start = s_time.strftime("%Y-%m-%d %H:%M:%S")
    end = e_time.strftime("%Y-%m-%d %H:%M:%S")

    arg = [a.Wavelength(wavelength),
           a.vso.Source(source),
           a.Instrument(instrument),
           a.Time(start, end),
           a.Sample(12*u.hour)
           ]

    res = Fido.search(*arg)
    # get response object:
    table = res.tables[0]

    # get time string of final end time of results
    if len(table) == 0:
        print(f"{s_time} to {e_time}: Empty table")
        if e_time >= f_time:
            print("finish on empty table")
            break
        else:
            s_time = e_time
            e_time += step_time
            continue

    times = []
    for t in table["Start Time"]:
        t = t[0]
        # account for leap second in 2016
        if t == "2016-12-31 23:59:60":
            time = "2017-01-01 00:00:00"
        else:
            time = t
        times.append(datetime.strptime(time, fmt))
    times = np.array(times)

    index, dates = get_index(times, s_time, e_time, cadence)
    # get response
    vso_response = list(res.responses)[0]
    block = vso_response._data

    block = [block[k] for k in index]

    q = QueryResponse(block)
    # build unified responce object from sliced query responce
    UR = UnifiedResponse(q)
    print(UR)
    downloaded_files = Fido.fetch(UR, path=path, progress=False)

    s_time = e_time + cadence
    if s_time > f_time:
        break
    e_time = s_time + step_time

