import requests  # to get image from the web
import shutil  # to save it locally
import os

main_url = "http://www.srl.caltech.edu/STEREO2/Position/ahead/"
folder = "DATA/stereo_pos_data/"
os.makedirs(folder) if not os.path.exists(folder) else None

"""
Heliocentric Earth equatorial (HEEQ)
This system has its Z axis parallel to the Sun's rotation axis
(positive to the North) and its X axis towards the intersection
of the solar equator and the solar central meridian as seen from
the Earth
"""

# get STEREO HEEQ data for 2006-2020:
for year in range(2006, 2021):
    name = f"position_ahead_{year}_HEEQ.txt"
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
