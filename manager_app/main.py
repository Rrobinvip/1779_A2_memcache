from manager_app import app
from flask import render_template, url_for, request, redirect
from flask import flash, jsonify
import requests
from glob import escape

# Import Forms
from manager_app.form import ConfigForm, ClearForm, DeleteForm, ManualForm

# Import helper
from manager_app.helper import api_call

# Import aws controller
from manager_app.aws import AWSController
aws_controller = AWSController()

@app.route("/")
def manager_main():
    return redirect(url_for("status"))

@app.route("/status")
def status():
    return render_template("status.html", tag1_selected=True)

# TODO: need to update config and api_call to make them call instances. 
#       1. Acquire instances ipv4 address to make call.
#       2. Read response from instance. 
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
        # result = api_call("GET", "config", parms)

        # if result.status_code == 200:
        #     flash("Update success")
        # else: 
        #     flash("Update failed")
        flash("Update success")
        return redirect(url_for("memcache_config"))

    elif request.method == "POST" and config_form.validate_on_submit():
        size = config_form.size.data
        choice = config_form.replacement_policy.data

        parms = {"size":size, "replacement_policy":choice}
        # result = api_call("GET", "config", parms)

        # if result.status_code == 200:
        #     flash("Update success")
        # else: 
        #     flash("Update failed")
        flash("Update success")
        return redirect(url_for("memcache_config"))

    if request.method == "POST" and clear_form.validate_on_submit():
        # result = api_call("GET", "clear")

        # if result.status_code == 200:
        #     flash("memcache cleared")
        # else: 
        #     flash("Update failed")
        flash("memcache cleared")
        return redirect(url_for("memcache_config"))
        
    return render_template("config.html", form1=config_form, form2=clear_form, tag2_selected=True)

@app.route("/manual", methods=["GET", "POST"])
def manual_resizing():
    manual_form = ManualForm()

    status_dic = aws_controller.get_instances_status()
    result = False

    if request.method == "POST" and manual_form.validate_on_submit():
        if manual_form.refresh.data:
            return redirect(url_for("manual_resizing"))
        
        if manual_form.growing.data:
            result = aws_controller.instance_operation("growing", 1)
        else:
            result = aws_controller.instance_operation("shrinking", 1)

        if result['status_code'] == 200:
            flash("Operation success")
        else:
            flash("Operation failed.\nReasons can be either: No more intsances to stop/All instances are already running/Some pending instances.")
        

        return redirect(url_for("manual_resizing"))

    return render_template("manual.html", form1=manual_form, status_dic=status_dic)