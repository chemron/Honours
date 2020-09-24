import os

folder = "DATA/png_phase/"
for f_name in os.listdir(folder):
    splits = f_name.split("_")
    new_name = f"{splits[0]}_{splits[2]}_{splits[3]}"
    os.rename(folder + f_name, folder + new_name)


