import boto3
from manager_app.config import Config

class AWSController:
    ec2_resource = None
    ec2_client = None
    instance_list = None

    def __init__(self):
        '''
        instance_active_index: 2 for running, 1 for pending, 0 for stopped. 
        instance_active_status: index 0 for # of running instances, index 1 for # of pending instances, index 2 for # of stopped instances.
        '''
        self.ec2_resource = boto3.resource('ec2', region_name='us-east-1')
        self.ec2_client = boto3.client('ec2', region_name='us-east-1')
        self.instance_list = [self.ec2_resource.Instance(i) for i in Config.INSTANCE_ID]

    def reload_instance_status(self):
        '''
        Reload instance state. This method must be executed before any operations that requires live state of the instance. Instance state doesn't automatically update. 
        '''
        for i in self.instance_list:
            i.reload()

    def get_instances_status(self):
        '''
        Instance status doesn't update by themselves. They needed to by manually updated. This function will update their status and return a up to date list. 
        '''
        self.reload_instance_status()

        result = {}

        for i in self.instance_list:
            result.update({i.id:i.state['Name']})

        return result

    def instance_operation(self, commend, flag):
        '''
        commend: growing or shrinking.
        flag: 1 for grow/shrink 1 instance at a time. 0 for grow/shrink based on ratio 2/0.5.

        This method will turn instance on or off based on commend and flag. 

        ### Example:

        When `flag == 1`, `commend == 'growing', method will go through all instances, find one stopped instance and start it. If there has no 
        stopped instance, method will retun operation fail.

       When `flag == 0`, `commend == 'growing', method will check if there has enough space to grow. Operation fail will be returned if no enough instances satisfy 
       the growing ratie. Also when 'shrinking', method will make sure there has at least one instance running. 
        '''
        # Update instances status.
        self.reload_instance_status()

        if flag == 1:
            opertion_success = False
            if commend == "growing":
                for i in self.instance_list:
                    if i.state['Name'] == 'stopped':
                        i.start()
                        opertion_success = True
                        break
            else:
                for i in self.instance_list:
                    if i.state['Name'] == 'running':
                        i.stop()
                        opertion_success = True
                        break
            if opertion_success:
                return {"status_code":200, "operation_type":"single growing/shrinking", "message":"operation success"}
            else:
                return {"status_code":400, "operation_type":"single growing/shrinking", "message":"operation failed"}

        else:
            operation_success = False
            number_of_running_instances = 0
            number_of_stopped_instances = 0

            for i in self.instance_list:
                if i.state['Name'] == 'running':
                    number_of_running_instances+=1
                elif i.state['Name'] == 'stopped':
                    number_of_stopped_instances+=1

            if commend == 'growing':
                # conditional statement make sure there are enough space.
                if 2*number_of_running_instances <= len(self.instance_list):
                    for c in range(number_of_running_instances):
                        for i in self.instance_list:
                            if i.state['Name'] == 'stopped':
                                i.start()
                    operation_success = True
            else:
                if number_of_running_instances//2 != 0:
                    for c in range(number_of_running_instances-(number_of_running_instances-len(self.instance_list))):
                        for i in self.instance_list:
                            if i.state['Name'] == 'running':
                                i.stop()
                    operation_success = True
            
            if operation_success:
                return {"status_code":200, "operation_type":"ratio growing/shrinking", "message":"operation success"}
            else:
                return {"status_code":400, "operation_type":"ratio growing/shrinking", "message":"operation failed"}

    def get_ip_address(self):
        self.reload_instance_status()

        result = {}

        for i in self.instance_list:
            if i.state['Name'] != 'running':
                result.update({i.id:'0.0.0.0'})
            else:
                result.update({i.id:i.public_ip_address})
        
        return result

    def clear_s3(self):
        # TODO: remove all data inside S3.
        return 1

    def clear_RDS(self):
        # TODO: remove all entries from RDS.
        return 1