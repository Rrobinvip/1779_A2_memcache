from auto_scaler import app
import threading
import time
from auto_scaler.aws import AWSController
from ec2_metadata import ec2_metadata
from flask import jsonify

aws_controller = AWSController()



@app.before_first_request
def run_when_start():
    task = threading.Thread(target = cloud_watch)
    task.start()

def cloud_watch():
    while True:
        instancesStatus = aws_controller.get_instances_status()
        for status in instancesStatus:
            print(status)
        time.sleep(60)



@app.route("/initialize")
def initialize():
    '''
    This function is intend to call when start to initialize cloudwatch
    '''
    print("-----------------------------------Called-------------------------------------------")
    response = jsonify({
        "success":"true",
        "status":200
    })
    return response
