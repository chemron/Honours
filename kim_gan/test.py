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

parser.add_argument("--display_iter",
                    help="number of iterations between each test",
                    type=int,
                    default=20000
                    )
parser.add_argument("--max_iter",
                    help="total number of iterations",
                    type=int,
                    default=500000
                    )
parser.add_argument("--input",
                    help="input dataset",
                    type=str,
                    default="AIA"
                    )
args = parser.parse_args()


# set parameters
SLEEP_TIME = 1000
DISPLAY_ITER = args.display_iter
MAX_ITER = args.max_iter
MODE = 'AIA_to_HMI'
INPUT = args.input
OUTPUT = 'MAG'
OP1 = f'{INPUT.upper()}_to_{OUTPUT}'

TRIAL_NAME = args.model_name

TEST_PATH = f'./DATA/{INPUT.lower()}_test/*.npy'

ISIZE = 1024  # input size
NC_IN = 1  # number of channels in the output
NC_OUT = 1  # number of channels in the input
BATCH_SIZE = 1  # batch size


# finds and sorts the filenames for INPUT1, INPUT2 and OUTPUT respectively
IMAGE_LIST1 = sorted(glob.glob(TEST_PATH))

RESULT_PATH_MAIN = './RESULTS/' + TRIAL_NAME + '/'
# os.mkdir(RESULT_PATH_MAIN) if not os.path.exists(RESULT_PATH_MAIN) else None

# file path for the results of INPUT1 to OUTPUT (generating HMI from nearside)
RESULT_PATH1 = RESULT_PATH_MAIN + OP1 + '/'
os.makedirs(RESULT_PATH1) if not os.path.exists(RESULT_PATH1) else None


def GET_DATE_STR(file):
    # get name and remove extension
    filename = file.split("/")[-1][:-4]  # filename is at end of file path
    date_str = filename.split("_")  # date string is after first "_"
    date_str = f"{date_str[1]}_{date_str[2]}"
    return date_str


# during training, the model was saved every DISPLAY_ITER steps
# as such, test every DISPLAY_ITER.
ITER = DISPLAY_ITER
while ITER <= MAX_ITER:

    SITER = '%07d' % ITER  # string representing the itteration

    # file path for the model of current itteration
    MODEL_NAME = './MODELS/' + TRIAL_NAME + '/' + MODE + '/' + MODE + \
        '_ITER' + SITER + '.h5'

    # file path to save the generated outputs from INPUT1 (nearside)
    SAVE_PATH1 = RESULT_PATH1 + 'ITER' + SITER + '/'
    os.mkdir(SAVE_PATH1) if not os.path.exists(SAVE_PATH1) else None

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

    for i in range(len(IMAGE_LIST1)):
        # input image
        IMG = np.load(IMAGE_LIST1[i]) / 255.0 * 2 - 1

        DATE = GET_DATE_STR(IMAGE_LIST1[i])
        # reshapes IMG tensor to (BATCH_SIZE, ISIZE, ISIZE, NC_IN)
        IMG.shape = (BATCH_SIZE, ISIZE, ISIZE, NC_IN)
        # output image (generated HMI)
        FAKE = NET_G_GEN(IMG)
        FAKE = ((FAKE[0] + 1) / 2.0 * 255.).clip(0, 255).astype('uint8')
        FAKE.shape = (ISIZE, ISIZE) if NC_IN == 1 else (ISIZE, ISIZE, NC_OUT)
        SAVE_NAME = SAVE_PATH1 + OUTPUT + "_" + DATE
        np.save(SAVE_NAME, FAKE)

    del MODEL
    K.clear_session()

    ITER += DISPLAY_ITER
