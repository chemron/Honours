import os


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


dir = "/home/adonea/Mona0028/adonea/cameron/Honours/DATpythnA/"
prefix = "TRAIN"

for filename in os.listdir(dir):
    new_name = remove_prefix(filename, prefix)
    os.rename(dir + filename, dir + new_name)
