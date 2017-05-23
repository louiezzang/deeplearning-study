"""Classify the raw image.
author: Louie
"""
import sys
import tensorflow as tf

import cifar10
import config

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_integer('depth', 3, '')
tf.app.flags.DEFINE_integer('raw_height', 32, '')
tf.app.flags.DEFINE_integer('raw_width', 32, '')
tf.app.flags.DEFINE_string('checkpoint_dir', config.CHECKPOINT_DIR,
                           """Directory where to read model checkpoints.""")

def evaluate(img_path):
  """Eval CIFAR-10 for a number of steps."""
  with tf.Graph().as_default() as g:
    input_img = tf.image.decode_jpeg(tf.read_file(img_path), channels=FLAGS.depth)
    reshaped_image = tf.cast(input_img, tf.float32)

    # Image processing for evaluation.
    # Crop the central [height, width] of the image.
    resized_image = tf.image.resize_image_with_crop_or_pad(reshaped_image, FLAGS.raw_height, FLAGS.raw_width)

    # Subtract off the mean and divide by the variance of the pixels.
    float_image = tf.image.per_image_standardization(resized_image)

    # Set the shapes of tensors.
    float_image.set_shape([FLAGS.raw_height, FLAGS.raw_width, FLAGS.depth])

    # Create a fake batch of images (batch_size = 1)
    images = tf.expand_dims(float_image, 0)

    logits = cifar10.inference_one(images)
    _, top_k_pred = tf.nn.top_k(logits, k=config.NUM_LABEL_CLASSES)

    # Restore the moving average version of the learned variables for eval.
    variable_averages = tf.train.ExponentialMovingAverage(cifar10.MOVING_AVERAGE_DECAY)
    variables_to_restore = variable_averages.variables_to_restore()
    saver = tf.train.Saver(variables_to_restore)

    with tf.Session() as sess:
      # sess.run(tf.global_variables_initializer())
      ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
      if ckpt and ckpt.model_checkpoint_path:
        print("Check point : %s" % ckpt.model_checkpoint_path)
        # Restores from checkpoint
        saver.restore(sess, ckpt.model_checkpoint_path)
      else:
        print('No checkpoint file found')
        exit(0)

      _, top_indices = sess.run([_, top_k_pred])

      result = {}
      for key, value in enumerate(top_indices[0]):
        print(str(value) + ": " + str(_[0][key]))  # value: label index
        result[value] = _[0][key]

      return result

def main(argv):
  if len(argv) != 2:
    print 'Usage: classify.py <image filename>'
    sys.exit(2)

  img_path = argv[1]
  print "image:", img_path
  evaluate(img_path)


if __name__ == '__main__':
  tf.app.run()
