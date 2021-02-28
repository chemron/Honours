import glob
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


path = "/home/adonea/Mona0028/adonea/cameron/Honours/DATA"
folders = [f"{path}/TRAIN", f"{path}/TEST"]
types = ["MAG", "STE", "smap"]
types_joined = ["MAG", "STE", "smap"]
size = 1024


def make_plot(plot_name, n, arrs_individual=[], arrs_joined=None):
    n_rows = 1
    n_cols = n

    # if we want a blended image
    alpha = 0.55
    if arrs_joined is not None:
        n_cols += 1

    plt.figure(1, figsize=(5*n_cols, 5*n_rows))

    i = 1
    for arr in arrs_individual:
        plt.subplot(n_rows, n_cols, i)
        plt.imshow(arr, origin="lower", cmap='gray')
        i += 1

    if arrs_joined is not None:
        plt.subplot(n_rows, n_cols, n_cols)
        for arr in arrs_joined:
            plt.imshow(arr, origin="lower", alpha=alpha, cmap='gray')

    plt.tight_layout
    plt.savefig(plot_name)
    plt.close(1)


def load_numpy(file_strs):
    for file_str in file_strs:
        file = glob.glob(file_str)
        if len(file) == 1:
            filename = file[0]
            arr = np.load(filename)
            yield arr
        else:
            print(f"{len(file)} files matching: {file_str}")


for folder in folders:
    sub_folders = np.sort(glob.glob(f"{folder}/*"))
    for sub_folder in sub_folders:
        individual_file_strs = list([f"{sub_folder}/{type}*.npy"
                                     for type in types])
        # number of individual plots
        n = len(individual_file_strs)
        arrs_individual = load_numpy(individual_file_strs)
        joined_file_strs = [f"{sub_folder}/{type}*.npy"
                                 for type in types]
        arrs_joined = load_numpy(individual_file_strs)
        plot_name = f"{sub_folder}/combined.png"
        print(plot_name)
        make_plot(plot_name, n, arrs_individual, arrs_joined)
