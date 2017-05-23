"""Classify the raw images.
author: Louie
"""

import os, sys, getopt
import MySQLdb
import urllib
import config as cfg
from cifar10 import *

labels = ["food", "people", "face", "promo", "ambience"]

# Get configuration.
cfgpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.properties')
config = cfg.read_config([cfgpath])
db_url = config.get('mysql.kimchi', 'db_url')
db_user = config.get('mysql.kimchi', 'db_user')
db_password = config.get('mysql.kimchi', 'db_password')
db_name = config.get('mysql.kimchi', 'db_name')
tmp_image_dir = config.get('global', 'tmp_image_dir')

def classify_images(fetch_date):
  db = MySQLdb.connect(db_url, db_user, db_password, db_name)
  cursor = db.cursor()

  sql = "SELECT id, media_id, thumbnail_image, low_resolution_image, \
          standard_resolution_image, approval_status FROM coll_instagram_media \
          WHERE approval_stauts = '%s' \
          AND first_fetch_date >= '%s'" \
        % ('Pending', fetch_date)

  print "sql:", sql

  try:
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
      id = row[0]
      media_id = row[1]
      thumbnail_image = row[2]
      low_resolution_image = row[3]
      standard_resolution_image = row[4]
      approval_status = row[5]
      #label_train = row[6]

      print "id=%s, media_id=%s, low_resolution_image=%s, approval_status=%s" % \
            (id, media_id, low_resolution_image, approval_status)

      # Classify image.
      classify_image(media_id, low_resolution_image, fetch_date)
  except:
    print "Error: unable to fetch data"
    #raise

  db.close()

def classify_image(img_id, img_url, fetch_date):
  dest_dir = tmp_image_dir + "/" + fetch_date
  if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

  img_filename = dest_dir + "/" + img_id + ".jpg"
  if not os.path.exists(img_filename):
    urllib.urlretrieve(img_url, img_filename)

  predicted_labels = classify.evaluate(img_filename)
  print "image =", img_url
  print "*** predicted_labels =", predicted_labels

def main(argv):
  classify_images("2017-05-18")

if __name__ == '__main__':
  main(sys.argv[1:])