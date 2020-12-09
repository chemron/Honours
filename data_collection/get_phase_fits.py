import requests  # to get image from the web
import shutil  # to save it locally
from datetime import timedelta, datetime
import os


# Set up the image URL and filename
main_url = "http://jsoc.stanford.edu/data/farside/Phase_Maps/"

# files are formated as: PHASE_MAP_yyyy.mm.dd_hh:mm:ss.fits
start_date = datetime(2010, 4, 24)

end_date = datetime(2014, 9, 8)
dt = timedelta(hours=12)

folder = "./DATA/fits_phase_maps/"
os.makedirs(folder) if not os.path.exists(folder) else None

# http://jsoc.stanford.edu/data/farside/Phase_Maps/2010/PHASE_MAP_2010.04.25_00:00:00.fits
date = start_date
while date <= end_date:
    print(f"{date}\r", end="")
    name = f"PHASE_MAP_{date.year}.{date.month:0>2}." \
           f"{date.day:0>2}_{date.hour:0>2}:00:00.fits"

    url = f'{main_url}/{date.year}/{name}'
    filename = folder + name
    # Open the url image and stream content.
    r = requests.get(url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    else:
        print(f'{name} Couldn\'t be retreived')

    date += dt
