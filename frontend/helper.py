import requests
from frontend.config import LOCAL_CACHE_DIR, LOCAL_UPLOADS_DIR, ALLOWED_EXTENSIONS
import os
import base64
from datetime import datetime

def api_call(type, commend, params=None):
    '''
    This function is used to use the api. \n
    The flag will need to be updated in the future to accommodate different api's.
    '''
    request_url = "http://127.0.0.1:5000/backend/"
    url = request_url+commend
    print(" - Frontend.helper.api_call: ", url)
    if type == "GET":
        return requests.get(url, params, timeout=0.5)
    elif type == "POST":
        return requests.post(url, params, timeout=0.5)

def write_img_local(filename, decode_value):
    '''
    This function is used to decode the image and save it to the local path.
     - filename: The name of the file used to store the image.
     - decode_value: Images encrypted with decode64.
    '''
    final_path = os.path.join(LOCAL_CACHE_DIR, filename)
    image_decode = base64.b64decode(decode_value)
    print(" - Frontend.helper.write_img_local v:final_path ", final_path)
    file = open(final_path, "wb")
    file.write(image_decode)
    file.close

def image_encoder(filename):
    '''
    This function is used to create a encoded string with given image.
     - filename: The name of the file used to store the image.
    '''
    final_path = os.path.join(LOCAL_UPLOADS_DIR, filename)
    file = open(final_path, "rb")
    encode_string = base64.b64encode(file.read())
    return encode_string

def current_datetime():
    '''
    This function will return a fixed 'datetime' entry which can be inserted into sql.
    '''
    now = datetime.now()
    fixed_now = now.strftime('%Y-%m-%d %H:%M:%S')
    return fixed_now

def api_key_content(filename,decode_value):
    '''
    This function is intented for the api key test function.
    If the decode_value is not None, then it will return the decode value.
    If the decode is None, it will read the image file from the upload dir and encoded it to 64base
    '''
    if decode_value is not None:
        return decode_value
    else:
        final_path = os.path.join(LOCAL_UPLOADS_DIR,filename)
        file = open(final_path,'rb')
        encode_string = base64.b64encode(file.read())
    return encode_string

def api_image_store(file,filename):
    '''
    This function will save the image file from test api to local upload folder
    '''
    final_path = os.path.join(LOCAL_UPLOADS_DIR,filename)
    file.save(final_path)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
