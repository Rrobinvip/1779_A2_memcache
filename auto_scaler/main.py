from auto_scaler import app
import threading
import time
from auto_scaler.aws import AWSController
from auto_scaler.cloudwatch import CloudWatch
from ec2_metadata import ec2_metadata
from flask import jsonify

aws_controller = AWSController()
cloud_watch = CloudWatch()


@app.before_first_request
def run_when_start():
    print('-----------Start-----------------------')
    task = threading.Thread(target = cloud_watch)
    task.start()

def cloud_watch():
    print("-----------Function Called----------------")
    while True:
        instances = aws_controller.activate_instances()
        for instance in instances:
            print(instance)
            result = cloud_watch.get_miss_rate()
        time.sleep(60)



@app.route("/initialize")
def initialize():
    '''
    This function is intend to call when start to initialize cloudwatch
    '''
    print("------------called-----------------")
    response = jsonify({
        "success":"true",
        "status":200
    })
    return response
