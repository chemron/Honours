import requests  # to get image from the web
import shutil  # to save it locally
from datetime import timedelta, datetime
import os


# Set up the image URL and filename
main_url = "http://jsoc.stanford.edu/data/farside/Phase_Maps/"

# files are formated as: PHASE_MAP_yyyy.mm.dd_hh:mm:ss.fits
start_date = datetime(2014, 9, 7)
# TODO: make this update to current day

end_date = datetime(2020, 8, 3)
dt = timedelta(hours=12)

folder = "./fits_phase_maps/"
os.makedirs(folder) if not os.path.exists(folder) else None


date = start_date
while date <= end_date:
    print(f"{date}\r", end="")
    name = f"PHASE_MAP_{date.year}.{date.month:0>2}." \
           f"{date.day:0>2}_{date.hour:0>2}:00:00.fits"

    url = main_url + name
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
