import datetime
import boto3
import base64

class CloudWatch:
    
    cloudClient = None

    def __init__(self):
        self.cloudClient = boto3.client(
            'cloudwatch',
            region_name = 'us-east-1'
        )
        
    def get_metrics_image(self):
        metrices_list = ['HitRate', 'MissRate', 'NumberOfItem', 'NumberOfRequest', 'TotalSize']
        result = []
        
        for i, e in enumerate(metrices_list):
            response = self.cloudClient.get_metric_widget_image(
                MetricWidget='''
                {{
                "view": "timeSeries",
                "stacked": false,
                "metrics": [
                    [ "ece1779/a2", "{}", "Instance ID", "i-0004e5771db2385a4", {{ "region": "us-east-1" }} ],
                    [ "...", "i-001617701b24b9f15", {{ "region": "us-east-1" }} ],
                    [ "...", "i-00919b1cebd5badef", {{ "region": "us-east-1" }} ],
                    [ "...", "i-0396c8e9d90a99bf8", {{ "region": "us-east-1" }} ],
                    [ "...", "i-0522fc067719b7e7b", {{ "region": "us-east-1" }} ],
                    [ "...", "i-0ab55e23171dd000d", {{ "region": "us-east-1" }} ],
                    [ "...", "i-0c7bc72034eca6538", {{ "region": "us-east-1" }} ],
                    [ "...", "i-0deec7aa32d788514", {{ "region": "us-east-1" }} ]
                ],
                "width": 1000,
                "height": 200,
                "start": "-PT3H",
                "end": "P0D",
                "timezone": "-0500"
            }}'''.format(e),
                OutputFormat='png'
            )
            string = base64.b64encode(response['MetricWidgetImage']).decode('utf-8')
            result.append(string)
        return result
    
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
        # print(" - manager.cloudwatch: Miss rate:")
        
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
        # print(results)
        for result in results:
            datapoint = result['Datapoints']
            # print("Datapoint: {}".format(datapoint))
            #The datapoints for this instance is 0
            #It either not initialized or has not sent any data yet
            if len(datapoint) == 0:
                continue
            else :
                numberOfDataPoints = numberOfDataPoints + 1
                # print(datapoint[0]['Average'])
                sumMissRate = sumMissRate + datapoint[0]['Average']
        #There is no datapoint at cloud watch
        if numberOfDataPoints == 0:
            # print("No Datapoint at cloud watch")
            return 0.0
        else:
            # print( "\t - manager.cloudwatch : v:sumMissRate {} v:numberOfDataPoints {}".format(sumMissRate, numberOfDataPoints))
            return sumMissRate/numberOfDataPoints
    
    def get_hit_rate(self, instances):
        '''
        This function is used by manager to calculate the average hit rate of all instances

        Params:
        instances: running instance id list
        '''
        results = []
        numberOfDataPoints = 0
        sumHitRate = 0.0
        # print(" - manager.cloudwatch: Hit rate:")
        for instance in instances:
            result = self.cloudClient.get_metric_statistics(
                Namespace = 'ece1779/a2',
                MetricName = 'HitRate',
                Dimensions = [{
                    'Name':'Instance ID',
                    'Value': instance
                }],
                StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 60),
                EndTime = datetime.datetime.utcnow(),
                Period = 60,
                Statistics = ['Average'],
                Unit = 'Percent'
            )
            results.append(result)
        # print("----------------Hit Rate Result-------------------------")
        # print(results)
        for result in results:
            datapoint = result['Datapoints']
            # print("Datapoint : {}".format(datapoint))

            if len(datapoint) == 0:
                continue
            else:
                numberOfDataPoints = numberOfDataPoints + 1
                # print(datapoint[0]['Average'])
                sumHitRate = sumHitRate + datapoint[0]['Average']
        if numberOfDataPoints == 0:
            # print("No Hit Rate Datapoint at cloud watch")
            return 0.0
        else:
            # print( "\t - manager.cloudwatch : v:sumHitRate {} v:numberOfDataPoints {}".format(sumHitRate, numberOfDataPoints))
            return sumHitRate/numberOfDataPoints
    
    def get_number_of_item(self, instances):
        '''
        This function is used by manager to calculate the average number of item on memcache

        Params:
        instances: running instance id list
        '''
        results = []
        numberOfDataPoints = 0
        sumNumber = 0.0
        # print(" - manager.cloudwatch: # of item:")
        
        for instance in instances:
            result = self.cloudClient.get_metric_statistics(
                Namespace = 'ece1779/a2',
                MetricName = 'NumberOfItem',
                Dimensions = [{
                    'Name':'Instance ID',
                    'Value':instance
                }],
                StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 60),
                EndTime = datetime.datetime.utcnow(),
                Period = 60,
                Statistics = ['Average'],
                Unit = 'Count'
            )
            results.append(result)
        # print("----------------Number of Item----------------")
        # print(results)
        for result in results:
            datapoint = result['Datapoints']
            # print("Datapoint : {}".format(datapoint))

            if len(datapoint) == 0:
                continue
            else:
                numberOfDataPoints = numberOfDataPoints + 1
                # print(datapoint[0]['Average'])
                sumNumber = sumNumber + datapoint[0]['Average']
            if numberOfDataPoints == 0:
                # print("No Number of Item Datapoint at cloud watch")
                return 0.0
            else:
                # print( "\t - manager.cloudwatch : v:sumNumber {} v:numberOfDataPoints {}".format(sumNumber, numberOfDataPoints))
                return sumNumber/numberOfDataPoints
    
    def get_total_size_of_item(self, instances):
        '''
        This function is used by manager to calculate the average size of item on memcache

        Params:
        instances: running instance id list
        '''
        results = []
        numberOfDataPoints = 0
        sumSize = 0.00
        # print(" - manager.cloudwatch: total size of item:")
        for instance in instances:
            result = self.cloudClient.get_metric_statistics(
                Namespace = 'ece1779/a2',
                MetricName = 'TotalSize',
                Dimensions = [{
                    'Name':'Instance ID',
                    'Value':instance
                }],
                StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 60),
                EndTime = datetime.datetime.utcnow(),
                Period = 60,
                Statistics = ['Average'],
                Unit = 'Bytes'
            )
            results.append(result)
        # print("---------------Total Size-----------------")
        # print(results)
        for result in results:
            datapoint = result['Datapoints']
            # print("Datapoint: {}".format(datapoint))

            if len(datapoint) == 0:
                continue
            else:
                numberOfDataPoints = numberOfDataPoints + 1
                # print(datapoint[0]['Average'])
                sumSize = sumSize + datapoint[0]['Average']
            if numberOfDataPoints == 0:
                # print("No Total Size Datapoint at cloud watch")
                return 0
            else:
                # print( "\t - manager.cloudwatch : v:sumSize {} v:numberOfDataPoints {}".format(sumSize, numberOfDataPoints))
                return sumSize/numberOfDataPoints
    
    def get_total_number_of_requests(self, instances):
        '''
        This function is used by manager to calculate the average request/min of all instances

        Params:
        instances: running instance id list
        '''
        results = []
        numberOfDataPoints = 0
        numberOfRequest = 0.00
        # print(" - manager.cloudwatch: total size of item:")
        for instance in instances:
            result = self.cloudClient.get_metric_statistics(
                Namespace = 'ece1779/a2',
                MetricName = 'NumberOfRequest',
                Dimensions = [{
                    'Name':'Instance ID',
                    'Value':instance
                }],
                StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 60),
                EndTime = datetime.datetime.utcnow(),
                Period = 60,
                Statistics = ['Average'],
                Unit = 'Count'
            )
            results.append(result)
        # print("---------------Number of Request----------------")
        # print(results)
        for result in results:
            datapoint = result['Datapoints']
            # print("Datapoint : {}".format(datapoint))

            if len(datapoint) == 0:
                continue
            else:
                numberOfDataPoints = numberOfDataPoints + 1
                # print(datapoint[0]['Average'])
                numberOfRequest = numberOfRequest + datapoint[0]['Average']
            if numberOfRequest == 0:
                # print("No Request Number Datapoint at cloud watch")
                return 0
            else:
                # print( "\t - manager.cloudwatch : v:# requests {} v:numberOfDataPoints {}".format(numberOfRequest, numberOfDataPoints))
                return numberOfRequest/numberOfDataPoints


            




    

