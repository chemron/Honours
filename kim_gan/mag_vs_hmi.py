import numpy as np
from PIL import Image
import os

x = "AIA"  # test input
y = "HMI"  # test output
g = "MAG"  # generator output
model = "P100_1"

input_test_dir = f"DATA/{x.lower()}_test/"
output_test_dir = f"DATA/{y.lower()}_test/" if y is not None else None
result_dir = f"RESULTS/{model}/{x}_to_{g}/"

png_dir = f"RESULTS/{model}/{x}_to_{g}_PNG/"

os.makedirs(png_dir) if not os.path.exists(png_dir) else None

iters = np.sort(os.listdir(result_dir))


def join_images(filename, pngs):
    images = [Image.fromarray(np.load(x)) for x in pngs]

    widths, heights = zip(*(i.size for i in images))

    max_height = max(heights)
    for i in range(len(images)):
        if heights[i] < max_height:
            im_ratio = round(widths[i]/heights[i])
            images[i] = images[i].resize((max_height*im_ratio, max_height))

    widths = [i.width for i in images]
    total_width = sum(widths)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(filename)


def GET_DATE_STR(file):
    # get name and remove extension
    filename = file.split("/")[-1][:-4]  # filename is at end of file path
    date_str = filename.split("_")  # date string is after first "_"
    date_str = f"{date_str[1]}_{date_str[2]}"
    return date_str


for iter in iters:
    path = result_dir + iter + "/"
    files = np.sort(os.listdir(path))
    for filename in files:
        mag = path + filename
        date = GET_DATE_STR(mag)
        # input file of gan with same date
        x_file = f"{input_test_dir}{x}_{date}.npy"
        y_file = f"{output_test_dir}{y}_{date}.npy" if y is not None else None

        pngs = [x_file]

        if y is not None:
            if os.path.isfile(y_file):
                pngs.append(y_file)

        pngs.append(mag)

        print(*pngs)

        join_images(png_dir, pngs)
