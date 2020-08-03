import requests  # to get image from the web
import shutil  # to save it locally

# Set up the image URL and filename
image_url = "https://miro.medium.com/max/700/1*G0pnrpiSVN01EZCGXiHkYQ.jpeg"

# Open the url image, set stream to True, this will return the stream content.
r = requests.get(image_url, stream=True)

# Check if the image was retrieved successfully
if r.status_code == 200:
    r.raw.decode_content = True

    # Open a local file with wb ( write binary ) permission.
    with open("test.jpeg", 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    print('Image sucessfully Downloaded')
else:
    print('Image Couldn\'t be retreived')
