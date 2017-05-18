"""Converts the raw images to cifar input data format.
author: Louie
"""

import os
import tensorflow as tf
import random
#import matplotlib

# matplotlib.use('Qt5Agg')
#matplotlib.use('tkagg')
#import matplotlib.pyplot as plt
import numpy as np

import config

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('data_dir', config.DATA_DIR, '')
tf.app.flags.DEFINE_string('image_dir', config.IMAGE_DIR, '')
tf.app.flags.DEFINE_integer('depth', 3, '')
tf.app.flags.DEFINE_integer('raw_height', 32, '')
tf.app.flags.DEFINE_integer('raw_width', 32, '')


def get_filename_set(data_set):
  labels = []
  filename_set = []

  with open(FLAGS.image_dir + '/labels.txt') as f:
    for line in f:
      inner_list = [elt.strip() for elt in line.split(',')]
      labels += inner_list

  for i, label in enumerate(labels):
    list = os.listdir(FLAGS.image_dir + '/' + data_set + '/' + label)
    for filename in list:
      filename_set.append([i, FLAGS.image_dir + '/' + data_set + '/' + label + '/' + filename])

  random.shuffle(filename_set)
  return filename_set


def read_jpeg(filename):
  value = tf.read_file(filename)
  decoded_image = tf.image.decode_jpeg(value, channels=FLAGS.depth)
  resized_image = tf.image.resize_images(decoded_image, [FLAGS.raw_height, FLAGS.raw_width])
  resized_image = tf.cast(resized_image, tf.uint8)

  return resized_image


def convert_images(sess, data_set):
  filename_set = get_filename_set(data_set)

  dest_directory = FLAGS.data_dir + '/cifar-10-batches-bin'
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)

  if data_set == 'train':
    data_filename = dest_directory + '/' + 'data_batch_1.bin'
  else:
    data_filename = dest_directory + '/' + 'test_batch.bin'
  with open(data_filename, 'wb') as f:
    print data_set
    for i in range(0, len(filename_set)):
      resized_image = read_jpeg(filename_set[i][1])

      try:
        image = sess.run(resized_image)
      except Exception as e:
        print e.message
        continue

      #plt.imshow(np.reshape(image.data, [FLAGS.raw_height, FLAGS.raw_width, FLAGS.depth]))
      #plt.show()

      print i, filename_set[i][0], image.shape, filename_set[i][1]
      f.write(chr(filename_set[i][0]))
      f.write(image.data)


def read_raw_images(sess, data_set):
  if data_set == 'train':
    data_filename = FLAGS.data_dir + '/cifar-10-batches-bin/' + 'data_batch_1.bin'
  else:
    data_filename = FLAGS.data_dir + '/cifar-10-batches-bin/' + 'test_batch.bin'

  filename = [data_filename]
  filename_queue = tf.train.string_input_producer(filename)

  record_bytes = (FLAGS.raw_height) * (FLAGS.raw_width) * FLAGS.depth + 1
  reader = tf.FixedLengthRecordReader(record_bytes=record_bytes)
  key, value = reader.read(filename_queue)
  record_bytes = tf.decode_raw(value, tf.uint8)

  tf.train.start_queue_runners(sess=sess)

  for i in range(0, 100):
    result = sess.run(record_bytes)
    print i, result[0]
    image = result[1:len(result)]

    #plt.imshow(np.reshape(image, [FLAGS.raw_height, FLAGS.raw_width, FLAGS.depth]))
    #plt.show()


def main(argv=None):
  with tf.Session() as sess:
    convert_images(sess, 'train')
    convert_images(sess, 'eval')
    # read_raw_images(sess, 'eval')


if __name__ == '__main__':
  tf.app.run()
