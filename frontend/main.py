# from crypt import methods
# from fileinput import filename
# from stat import filemode
# from telnetlib import SE
# from traceback import clear_frames

from glob import escape
from tkinter.messagebox import NO
from flask import render_template, url_for, request, redirect
from flask import flash, jsonify
from frontend import app
import requests
import logging
from datetime import datetime

# Picture upload form
from frontend.form import UploadForm, pictures

# Data model
from frontend.data import Data

# Search form
from frontend.form import SearchForm

# Config form 
from frontend.form import ConfigForm
from frontend.form import ClearForm

# Helper
from frontend.helper import api_call, api_image_store, allowed_file

# Encode and decode img
from frontend.helper import write_img_local, image_encoder, current_datetime


sql_connection = Data()

@app.before_first_request
def start():
    '''
    This function calls the backend statistics before the first request. 
    And it will also detect if frontend and backend is working properly. 
    '''
    r = api_call("GET", "statistics")
    print("Response: ", r)
    if r.status_code == 200:
        print(" * Frontend and backend connection success.")
    pass

@app.route('/')
def main():
    return redirect(url_for("upload_picture"))

#This function is front back call example
@app.route('/test')
def test():
    # It's probably not working. 
    #call the backend url
    request = requests.get("http://127.0.0.1:5000/backend/test",timeout = 5)
    #parse the json file
    result = request.json()
    #access content in json file
    print(result["success"])
    print(result["status"])
    print(result["message"])
    return "This is front end test"
    
@app.route('/upload', methods=["GET", "POST"])
def upload_picture():
    '''
    This function allows user to upload images. 
    It will first save the image to local file system. Then it will encode the image with base64. After encoding, it 
    will post reletive data to memcache for quick access. Image stores in different systems in following methods:
    ### SQL:
        * key
        * filename
        * upload_time

    ### memcache:
        * key
        * base64 encoded value of image
        * upload_time
    '''
    picture_form = UploadForm()

    if request.method == "POST" and picture_form.validate_on_submit():
        filename = pictures.save(picture_form.pictures.data)
        key = picture_form.key.data

        # Frontend will encode the image into a string, and pass it to backend as a value. 
        value = image_encoder(filename)
        upload_time = current_datetime()
        parms = {"key":key, "value":value, "upload_time":upload_time}
        result = api_call("POST", "put", parms)

        if result.status_code == 200:
            print(" - Frontend: backend stores image into memcache.")
        else:
            print(" - Frontend: memcache failed to store image for some reason. Check message from 'backend.memcache.*' for more help. Image will still be stored locally. ")

        # After update it with the memcache, frontend will add filename and key into db. 
        flash("Upload success")
        print(filename, key)
        sql_connection.add_entry(key, filename)
        return redirect(url_for("upload_picture"))
    
    return render_template("upload.html", form=picture_form)

@app.route("/search", methods=["GET", "POST"])
def search_key():
    '''
    This function is used to search for the key entered by the user.

    Workflow: The frontend will first initiate a search with the back end, if the backend returns an error code 400, 
    the frontend will initiate a search to the database. If the backend returns code 200, the frontend will decode the 
    backend image and store it in the local cache. No matter what the result is, if there is an image matching the user's 
    search key, it will be displayed on the web page.

    Image from SQL (filename) will be directly retrieved from `/static/uploads`, image from memcache will be decoded and stored in 
    `/static/local_cache`. Image must be cached locally to be rendered in HTML. 
    '''
    search_form = SearchForm()
    filename = None
    upload_time = None
    key = None
    cache_flag = False

    print("* Search init...")
 
    # Get key through different approaches. 
    if (request.method == "GET" and "key" in request.args):
        key = escape(request.args.get("key"))
        # Call backend
        print(" - Frontend.main.search_key : Searching in memcache..")
        data = api_call("GET", "get", {"key":key})

        # If the backend misses, look up the database. If the backend hits, decrypt the image and store it
        if data.status_code == 400:
            print("\t Backend doesn't hold this value, try search in DB..")
            data = sql_connection.search_key(key)
            if len(data) == 0:
                print("\t DB doesn't hold this value. Search end.")
                flash("No image with this key.")
            else:
                filename = data[0][2]
                upload_time = data[0][3]
                print("Filename: {} upload_time: {}".format(filename, upload_time))

                # When data is retrieved from DB, add it to memcache.
                value = image_encoder(filename)
                parms = {"key":key, "value":value, "upload_time":upload_time}
                result = api_call("POST", "put", parms)

                if result.status_code == 200:
                    print(" - Frontend: backend stores image into memcache.")
                else:
                    print(" - Frontend: memcache failed to store image for some reason. Check message from 'backend.memcache.*' for more help. Image will still be stored locally. ")

        elif data.status_code == 200:
            data = data.json()
            value = data["value"]
            upload_time = data["upload_time"]

            # Add datetime prefix to image cache file.
            date_prefix = current_datetime()
            print(" - Frontend.main.search_key v:data_prefix ",date_prefix)
            filename = "image_local_"+key+"_"+date_prefix+".png"

            write_img_local(filename, value)
            cache_flag = True
            print(" - Frontend.main.search_key: v:Filename: {} v:upload_time: {}".format(filename, upload_time))
    elif request.method == "POST" and search_form.validate_on_submit():
        key = search_form.key.data

        # Call backend
        print(" - Frontend.main.search_key : Searching in memcache..")
        data = api_call("GET", "get", {"key":key})

        # This part, where requesting data from memcache, is exactly same as above. Becaause I don't have any good 
        # ideas to put them into a function. 

        # If the backend misses, look up the database. If the backend hits, decrypt the image and store it
        if data.status_code == 400:
            print("\t Backend doesn't hold this value, try search in DB..")
            data = sql_connection.search_key(key)
            if len(data) == 0:
                print("\t DB doesn't hold this value. Search end.")
                flash("No image with this key.")
            else:
                filename = data[0][2]
                upload_time = data[0][3]
                print("Filename: {} upload_time: {}".format(filename, upload_time))

                # When data is retrieved from DB, add it to memcache.
                value = image_encoder(filename)
                parms = {"key":key, "value":value, "upload_time":upload_time}
                result = api_call("POST", "put", parms)

                if result.status_code == 200:
                    print(" - Frontend: backend stores image into memcache.")
                else:
                    print(" - Frontend: memcache failed to store image for some reason. Check message from 'backend.memcache.*' for more help. Image will still be stored locally. ")

        elif data.status_code == 200:
            data = data.json()
            value = data["value"]
            upload_time = data["upload_time"]

            # Add datetime prefix to image cache file.
            date_prefix = current_datetime()
            print(" - Frontend.main.search_key v:data_prefix ",date_prefix)
            filename = "image_local_"+key+"_"+date_prefix+".png"

            # filename = "image_local_"+key+".png"

            write_img_local(filename, value)
            cache_flag = True
            print(" - Frontend.main.search_key: v:Filename: {} v:upload_time: {}".format(filename, upload_time))


    return render_template("search.html", 
                           form = search_form, 
                           tag1_selected=True, 
                           filename=filename, 
                           upload_time=upload_time,
                           key=key,
                           cache_flag=cache_flag)

@app.route("/allpairs")
def all_pairs():
    '''
    Show all pairs. 
    '''
    data = sql_connection.inspect_all_entries()
    return render_template("all_pairs.html", items=data, tag2_selected=True)


@app.route("/config", methods=["GET", "POST"])
def memcache_config():
    '''
    This function basically has two parts. First for updating memcache size and replacement policy, another for clear the memcache. 

    Two parts are triggered with different form. 
    '''
    config_form = ConfigForm()
    clear_form = ClearForm()

    # Give a default memcache size and replacement_policy, just in case database has nothing. 
    size = 100.0
    choice = 1

    if request.method == "GET" and "size" in request.args and "policy" in request.args:
        size = escape(request.args.get("size"))
        choice = escape(request.args.get("choice", type=int))
        parms = {"size":size, "replacement_policy":choice}
        result = api_call("GET", "config", parms)

        if result.status_code == 200:
            flash("Update success")
        else: 
            flash("Update failed")
        return redirect(url_for("memcache_config"))


    elif request.method == "POST" and config_form.validate_on_submit():
        size = config_form.size.data
        choice = config_form.replacement_policy.data

        parms = {"size":size, "replacement_policy":choice}
        result = api_call("GET", "config", parms)

        if result.status_code == 200:
            flash("Update success")
        else: 
            flash("Update failed")
        return redirect(url_for("memcache_config"))

    if request.method == "POST" and clear_form.validate_on_submit():
        result = api_call("GET", "clear")

        if result.status_code == 200:
            flash("memcache cleared")
        else: 
            flash("Update failed")
        return redirect(url_for("memcache_config"))
        
    return render_template("config.html", form1=config_form, form2=clear_form, tag3_selected=True)

@app.route("/status")
def memcache_status():
    '''
    Get all memcache status. 

    If data is empty, a dummy data will be given.
    '''
    data = sql_connection.get_stat_data()
    if data == None:
        data = [[0,0,0,0,0,0]]

    return render_template("status.html", items=data, tag4_selected=True)

@app.route("/api/list_keys", methods= ['POST'])
def api_list_keys():
    '''
    This function is for api test
    It will list all keys in the databases
    '''
    keys = sql_connection.get_keys()
    key_list = []
    if keys:
        for key in keys:
            key_list.append(key[0])
    return jsonify({
        "success":"true",
        "keys":key_list
    })

@app.route("/api/key/<key_value>", methods = ['POST'])
def api_key_search(key_value):
    #call backend
    print(" - Frontend.api_key_search: v:key_value", key_value)
    data = api_call("GET","get",{"key":key_value})

    #If the backend misses, look up the database
    if data.status_code == 400:
        result = sql_connection.search_key(key_value)
        #if the key does not exist in database, return error message
        if len(result) == 0:
            return jsonify({
                "success":"false",
                "error":{
                    "code":400,
                    "message":"Unknown Key Value"
                }
            })
        #if the key exists in database, retrive it from local file system
        else:
            filename = result[0][2]
            content = image_encoder(filename)
            content = content.decode()
            return jsonify({
                "success":"true",
                "content":content
            })
    elif data.status_code == 200:
        data = data.json()
        value = data["value"]
        return jsonify({
            "success":"true",
            "content":value
        })
    else:
        return jsonify({
            "Success":"false",
            "error":{
                "code":201,
                "message":"Unkown Error"
            }
        })

@app.route("/api/upload",methods = ['POST'])
def api_upload():
    key = request.form.get('key')
    file = request.files['file']
    filename = file.filename
    #if the request does not give file then return error code and message
    if filename == '':
        return jsonify({
            "success":"false",
            "error":{
                "code":400,
                "message":"No file given"
            }
        })
    
    if file and allowed_file(filename):
    #if we have the file then store the file to local
        api_image_store(file,filename)
        
        #front will encode the image and pass it to backend
        value = image_encoder(filename)
        upload_time = current_datetime()
        parms = {"key":key,"value":value,"upload_time":upload_time}
        result = api_call("POST","put",parms)

        if result.status_code == 200:
            print("Memcache image stored")
        else:
            print("Memcache error")
        
        sql_connection.add_entry(key,filename)
        return jsonify({
            "success":"true"
        })
    else:
        if not file:
            return jsonify({
                "success":"false",
                "error":{
                    "code":400,
                    "message":"No file given"
                }
            })
        if not allowed_file(filename):
            return jsonify({
                "success":"false",
                "error":{
                    "code":400,
                    "message":"File type not allowed"
                }
            })
        return jsonify({
                "success":"false",
                "error":{
                    "code":400,
                    "message":"Unknown error"
                }
        })

@app.route("/api/nocache/upload", methods=['POST'])
def api_nocache_upload():
    key = request.form.get('key')
    file = request.files['file']
    filename = file.filename
    
    if filename == '':
        return jsonify({
            "success":"false",
            "error":{
                "code":400,
                "message":"No file given"
            }
        })
    if file and allowed_file(filename):
        api_image_store(file,filename)
        sql_connection.add_entry(key,filename)
        return jsonify({
            "success":"true"
        })
    else:
        if not file:
            return jsonify({
                "success":"false",
                "error":{
                    "code":400,
                    "message":"No file given"
                }
            })
        if not allowed_file(filename):
            return jsonify({
                "success":"false",
                "error":{
                    "code":400,
                    "message":"File type not allowed"
                }
            })
        return jsonify({
            "success":"false",
            "error":{
                "code":400,
                "message":"Unknow error"
            }
        })

@app.route("/api/nocache/key/<key_value>", methods = ['POST'])
def api_nocache_key_search(key_value):
    result = sql_connection.search_key(key_value)
    if len(result) == 0:
        return jsonify({
            "success":"false",
            "error":{
                "code":400,
                "message":"Unknown Key Value"
            }
        })
    else:
        filename = result[0][2]
        content = image_encoder(filename).decode()
        return jsonify({
            "success":"true",
            "content":content
        })
