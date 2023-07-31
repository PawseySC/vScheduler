import logging
from vscheduler.lib.config import Credentials as MyCredentials

class Capture_log(object):
    """
    Logging class to call in methods and capture event 
    logs into separate files for booking and pool.
    """
    def __init__(self, flag, location):
        self.formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
        self.flag = flag
        self.location = location
    
    def extendable_logger(self, log_name, file_name, level=MyCredentials.log_level):
        handler = logging.FileHandler(file_name)
        handler.setFormatter(self.formatter) 
        specified_logger = logging.getLogger(log_name)
        specified_logger.setLevel(level)
        specified_logger.addHandler(handler)
        return specified_logger
    
    def log_pool(self):
        pool_logger = self.extendable_logger('pool_logs ' + self.location, '/home/ubuntu/visualisation_scheduler/vscheduler/log/pool.log')
        return pool_logger
    
    def log_booking(self):
        booking_logger = self.extendable_logger('booking_logs ' + self.location, '/home/ubuntu/visualisation_scheduler/vscheduler/log/booking.log')
        return booking_logger

    def log_socket(self):
        socket_logger = self.extendable_logger('socket_logs ' + self.location, '/home/ubuntu/visualisation_scheduler/vscheduler/log/socket.log')
        return socket_logger
    
    def log_db(self):
        database_logger = self.extendable_logger('database_logs ' + self.location, '/home/ubuntu/visualisation_scheduler/vscheduler/log/database.log')
        return database_logger
    
    def log_agent(self):
        agent_logger = self.extendable_logger(self.flag + " " + self.location, '/home/ubuntu/visualisation_scheduler/vscheduler/log/log.log')
        return agent_logger