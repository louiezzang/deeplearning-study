import os
import sys, getopt
import MySQLdb
import urllib
import config as cfg

# Get configuration.
cfgpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.properties')
config = cfg.read_config([cfgpath])
db_url = config.get('mysql.kimchi', 'db_url')
db_user = config.get('mysql.kimchi', 'db_user')
db_password = config.get('mysql.kimchi', 'db_password')
db_name = config.get('mysql.kimchi', 'db_name')
image_dir = config.get('global', 'image_dir')

def download_images(approval_status, label, tags, limit):
  """
  Downloads images to train.
  :param approval_status:
  :param label:
  :param tag:
  :param limit:
  :return:
  """
  db = MySQLdb.connect(db_url, db_user, db_password, db_name)
  cursor = db.cursor()

  condition = ""
  if approval_status == "Approved" or approval_status == "Rejected":
    condition = "approval_status = '" + approval_status + "'"

  i = 0
  tag_condion = "("
  for tag in tags.split(","):
    if i > 0:
      tag_condion += " OR "
    tag_condion += "tags LIKE '%" + tag + "%'"
    i += 1

  tag_condion += ")"

  if condition == "":
    condition = tag_condion
  else:
    condition = condition + " AND " + tag_condion

  sql = "SELECT id, media_id, thumbnail_image, low_resolution_image, \
          standard_resolution_image, approval_status FROM coll_instagram_media \
          WHERE %s \
          ORDER BY RAND() \
          LIMIT %s" \
          % (condition, limit)

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
      dest_dir = image_dir + "/" + label
      if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

      img_filename = dest_dir + "/" + media_id + ".jpg"
      if not os.path.exists(img_filename):
        urllib.urlretrieve(low_resolution_image, img_filename)
  except:
    print "Error: unable to fetch data"
    #raise

  db.close()


def main(argv):
  approval_status = ''
  label = 'none'
  tags = ''
  limit = 10
  try:
    opts, args = getopt.getopt(argv, "ha:l:t:n:", ["approval_status=", "label=", "tags=", "limit="])
  except getopt.GetoptError:
    print 'download_train_data.py -a <approval_status> -l <label> -t <tags> -n <limit>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print 'download_train_data.py -a <approval_status> -l <label> -t <tags> -n <limit>'
      sys.exit()
    elif opt in ("-a", "--approval_status"):
      approval_status = arg
    elif opt in ("-l", "--label"):
      label = arg
    elif opt in ("-t", "--tags"):
      tags = arg
    elif opt in ("-n", "--limit"):
      limit = arg

  if len(opts) != 4:
    print 'download_train_data.py -a <approval_status> -l <label> -t <tags> -n <limit>'
    sys.exit(2)

  print 'approval_status =', approval_status
  print 'label =', label
  print 'tags =', tags
  print 'limit =', limit

  download_images(approval_status, label, tags, limit)

if __name__ == '__main__':
  main(sys.argv[1:])


