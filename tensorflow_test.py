import numpy as np
import os
import glob
import time
from random import shuffle
from imageio import imread
import pandas as pd
import tensorflow as tf

import keras.backend as K
from keras.models import Model
from keras.layers import Conv2D, ZeroPadding2D, \
    BatchNormalization, Input, Dropout
from keras.layers import Conv2DTranspose, Activation, Cropping2D
from keras.layers import Concatenate
from keras.layers.advanced_activations import LeakyReLU
from keras.initializers import RandomNormal
from keras.optimizers import Adam
import argparse

print("Tensorflow version " + tf.__version__)
print(tf.config.list_physical_devices())

print(tf.reduce_sum(tf.random.normal([1000, 1000])))
