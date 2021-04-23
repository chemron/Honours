import os
import glob
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow.keras.backend as K
import tensorflow.compat.v1 as tf
import argparse


tf.disable_v2_behavior()
# initialise tensorflow
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
tf.Session(config=config)

# initialise KERAS_BACKEND
K.set_image_data_format('channels_last')
channel_axis = -1

# initialise os environment
os.environ['KERAS_BACKEND'] = 'tensorflow'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'


def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


parser = argparse.ArgumentParser()
parser.add_argument("--model_name",
                    help="name of model",
                    default='test_1'
                    )

parser.add_argument("--iter",
                    help="number of iterations between each test",
                    type=int,
                    default=100000
                    )

args = parser.parse_args()


# set parameters
SLEEP_TIME = 1000
ITER = args.iter
MODE = 'S_MAP_to_MAG'
INPUT = "smap"
OUTPUT = 'MAG'
OP1 = f'{INPUT.upper()}_to_{OUTPUT}'

TRIAL_NAME = args.model_name

MAIN_DIR = "/home/csmi0005/Mona0028/adonea/cameron/Honours/data_collection/DATA/"
TEST_PATH = f"{MAIN_DIR}np_phase_map/"
RESULT_PATH = f"/{MAIN_DIR}farside_mag/{TRIAL_NAME}/"
os.makedirs(RESULT_PATH) if not os.path.exists(RESULT_PATH) else None


ISIZE = 1024  # input size
NC_IN = 1  # number of channels in the output
NC_OUT = 1  # number of channels in the input
BATCH_SIZE = 1  # batch size


def GET_DATE_STR(file):
    # get name and remove extension
    filename = file[:-4]  # filename is at end of file path
    date_str = filename.split("_")  # date string is after first "_"
    date_str = f"{date_str[-2]}_{date_str[-1]}"
    return date_str


DATA_LIST = glob.glob(TEST_PATH + "*")

# during training, the model was saved every DISPLAY_ITER steps
# as such, test every DISPLAY_ITER.

SITER = '%07d' % ITER  # string representing the itteration

# file path for the model of current itteration
MODEL_NAME = './MODELS/' + TRIAL_NAME + '/' + MODE + '/' + MODE + \
    '_ITER' + SITER + '.h5'

# # file path to save the generated outputs from INPUT1 (nearside)
# SAVE_PATH1 = RESULT_PATH1 + 'ITER' + SITER + '/'
# os.mkdir(SAVE_PATH1) if not os.path.exists(SAVE_PATH1) else None

EX = 0
while EX < 1:
    if os.path.exists(MODEL_NAME):
        print('Starting Iter ' + str(ITER) + ' ...')
        EX = 1
    else:
        raise Exception('no model found at: ' + MODEL_NAME)

# load the model
MODEL = load_model(MODEL_NAME)

REAL_A = MODEL.input
FAKE_B = MODEL.output
# function that evaluates the model
NET_G_GENERATE = K.function([REAL_A], [FAKE_B])

# generates the output (HMI) based on input image (A)
def NET_G_GEN(A):
    output = [NET_G_GENERATE([A[i:i+1]])[0] for i in range(A.shape[0])]
    return np.concatenate(output, axis=0)

for image in DATA_LIST:
    DATE = GET_DATE_STR(image)
    SAVE_NAME = f"{OUTPUT}_{DATE}"


    if f'{SAVE_NAME}.npy' not in os.listdir(RESULT_PATH):
        SAVE_NAME = f"{RESULT_PATH}{SAVE_NAME}"

        # input image
        IMG = np.load(image) * 2 - 1

        # reshapes IMG tensor to (BATCH_SIZE, ISIZE, ISIZE, NC_IN)
        print(IMG.shape)
        print(np.min(IMG), np.max(IMG))
        IMG.shape = (BATCH_SIZE, ISIZE, ISIZE, NC_IN)
        # output image (generated HMI)
        FAKE = NET_G_GEN(IMG)
        FAKE = FAKE[0]
        if NC_IN == 1:
            FAKE.shape = (ISIZE, ISIZE)
        else:
            FAKE.shape = (ISIZE, ISIZE, NC_OUT)
        np.save(SAVE_NAME, FAKE)
    else:
        print(f"already tested on {image}")

del MODEL
K.clear_session()
