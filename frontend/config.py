import os

TEMPLATE_DIR = os.path.abspath("./frontend/templates")
STATIC_DIR = os.path.abspath("./frontend/static")
LOCAL_CACHE_DIR = os.path.abspath("./frontend/static/local_cache")
LOCAL_UPLOADS_DIR = os.path.abspath("./frontend/static/uploads")
LOCAL_S3_DL_DIR = os.path.abspath("./frontend/static/s3_download")
ALLOWED_EXTENSIONS = {'jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp'}

class Config(object):
    SECRET_KEY = "teeesssttt"
    UPLOADED_PHOTOS_DEST = "./frontend/static/uploads"
    # DB_CONFIG = {
    #     "user":"root",
    #     "password":"ece1779pass",
    #     "host":"localhost",
    #     "database":"cloudcomputing"
    # }
    DB_CONFIG = {
        "user":"root",
        "password":"19970808",
        "host":"localhost",
        "database":"memcache_test_1"
    }