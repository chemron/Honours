from PIL import Image
import os

im_dir = "DATA/png_stereo/"
files = os.listdir(im_dir)

for f in files:
    filename = f"{im_dir}{f}"
    im = Image.open(filename)
    im = im.rotate(180)
    im.save(filename)
