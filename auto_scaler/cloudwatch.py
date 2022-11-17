import time
import datetime
import boto3
from manager_app.config import Config

class CloudWatch:
    
    cloudClient = None

    def __init__(self):
        self.cloudClient = boto3.client(
            'cloudwatch',
            region_name = 'us-east-1'
        )
    
    def update_cloud_watch(self, instanceID, missRate):
        '''
        Used by backend node

        This function send miss rate to cloud watch from the backend node server.
        It will us instance id to distinish different instance

        Return: the reponse from cloudwatch server
        '''
        response = self.cloudClient.put_metric_data(
            MetricData = [{
                'MetricName': 'MissRate',
                'Dimensions':[{
                    'Name': 'Instance ID',
                    'Value': instanceID,
                }],
                'Unit':'Percent',
                'Value':missRate
            }],
            Namespace = 'ece1779/a2'
        )
        return response

    def get_miss_rate(self, instances):
        '''
        This function is used by auto scaler for calculate the average miss rate

        It will retrive the miss rate from cloudwatch, caluclate and return the average miss rate

        Note: It requires running instance list, when use this function, need to pass it running instance id
        '''
        results = []
        numberOfDataPoints = 0
        sumMissRate = 0.0
        for instance in instances:
            result = self.cloudClient.get_metric_statistics(
                Namespace = 'ece1779/a2',
                MetricName = 'MissRate',
                Dimensions = [{
                    'Name':'Instance ID',
                    'Value': instance,
                }],
                StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 60),
                EndTime = datetime.datetime.utcnow(),
                Period = 60,
                Statistics = ['Average'],
                Unit = 'Percent'
            )
            results.append(result)
        print(results)
        for result in results:
            datapoint = result['Datapoints']
            print("Datapoint: {}".format(datapoint))
            #The datapoints for this instance is 0
            #It either not initialized or has not sent any data yet
            if len(datapoint) == 0:
                continue
            else :
                numberOfDataPoints = numberOfDataPoints + 1
                print(datapoint[0]['Average'])
                sumMissRate = sumMissRate + datapoint[0]['Average']
        #There is no datapoint at cloud watch
        if numberOfDataPoints == 0:
            print("No Datapoint at cloud watch")
            return 0.0
        else:
            return sumMissRate/numberOfDataPoints

