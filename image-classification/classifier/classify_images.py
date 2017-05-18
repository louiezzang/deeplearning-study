import os, sys, getopt
import MySQLdb
import urllib
import config as cfg
from cifar10 import classify


labels = ["food", "people", "face", "promo", "ambience"]

# Get configuration.
cfgpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.properties')
config = cfg.read_config([cfgpath])
db_url = config.get('mysql.kimchi', 'db_url')
db_user = config.get('mysql.kimchi', 'db_user')
db_password = config.get('mysql.kimchi', 'db_password')
db_name = config.get('mysql.kimchi', 'db_name')
image_dir = config.get('global', 'image_dir')

def classify_images():
  img_url = ""
  img_filename = ""
  if not os.path.exists(img_filename):
    urllib.urlretrieve(img_url, img_filename)

  predicted_labels = classify.evaluate(img_filename)
  print "image =", img_url
  print "*** predicted_labels =", predicted_labels

def main(argv):
  classify_images()

if __name__ == '__main__':
  main(sys.argv[1:])