import tensorflow as tf
print("Tensorflow version " + tf.__version__)
print(tf.config.list_physical_devices('GPU'))
print(tf.reduce_sum(tf.random.normal([1000, 1000])))
