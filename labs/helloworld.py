'''
HelloWorld example using TensorFlow library.

Author: Louie
'''
import tensorflow as tf

# Create a Constant operation
hello = tf.constant('Hello, TensorFlow!')

# Start tf session
sess = tf.Session()

print(sess.run(hello))

a = tf.constant(10)
b = tf.constant(32)
print(sess.run(a + b))