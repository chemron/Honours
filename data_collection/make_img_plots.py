import glob
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


path = "/home/csmi0005/Mona0028/adonea/cameron/Honours/DATA"
types = ["STE", "smap", "MAG"]
types_joined = [] # ["MAG", "STE", "smap"]
gan_outputs = ["P100_32_kernal/"]
plot_all = False
size = 1024



def make_plot(plot_name, n, arrs_individual=[], arrs_joined=None):
    n_rows = (n-1)//4 + 1
    n_cols = 4

    # if we want a blended image
    alpha = 0.55
    if arrs_joined is not None:
        n_cols += 1

    plt.figure(1, figsize=(5*n_cols, 5*n_rows))

    i = 1
    for arr, name in arrs_individual:
        title = name.split("/")[-2][:-3]
        plt.subplot(n_rows, n_cols, i)
        plt.title(title)
        plt.imshow(arr, origin="lower", cmap='gray')
        i += 1

    if arrs_joined is not None:
        plt.subplot(n_rows, n_cols, n_cols)
        for arr, name in arrs_joined:
            plt.imshow(arr, origin="lower", alpha=alpha, cmap='gray')

    plt.tight_layout
    plt.savefig(plot_name)
    plt.close(1)


def load_numpy(file_strs):
    for file_str in file_strs:
        files = glob.glob(file_str)
        if not plot_all:
            files = files[-1:]
        if len(files) >= 1:
            for filename in files:
                arr = np.load(filename)
                yield arr, filename
        else:
            print(f"{len(files)} files matching: {file_str}")


for folder in ["TEST"]: #  "TRAIN"]:
    sub_folders = np.sort(glob.glob(f"{path}/{folder}/*"))
    for sub_folder in sub_folders:
        individual_file_strs = list([f"{sub_folder}/{t}*.npy"
                                     for t in types])
        if folder == "TEST":
            gan_files = list([f"{sub_folder}/{o}*.npy"
                              for o in gan_outputs])
            
            individual_file_strs += gan_files

        # number of individual plots
        data = list(load_numpy(individual_file_strs))
        n = len(data)

        info = ''
        if plot_all:
            info = '_all'
        plot_name = f"{sub_folder}/combined{info}.png"
        print(plot_name)
        make_plot(plot_name, n, data)
