
class Chart:
    hitRate = None
    numberOfItem = None
    totalSize = None
    numberOfRequest = None

    def __init__(self):
        self.hitRate = 0.0
        self.numberOfItem = 0.0
        self.totalSize = 0.0
        self.numberOfRequest = 0.0
    
    def set_hitRate(self, hitRate):
        self.hitRate = hitRate
    
    def get_hitRate(self):
        return self.hitRate
    
    def set_number_of_item(self, numberOfItem):
        self.numberOfItem = numberOfItem
    
    def get_number_of_item(self):
        return self.numberOfItem
    
    def set_total_size(self, totalSize):
        self.totalSize = totalSize
    
    def get_total_size(self):
        return self.totalSize
    
    def set_number_of_request(self, numberOfRequest):
        self.numberOfRequest = numberOfRequest
    
    def get_number_of_request(self):
        return self.numberOfRequest