import logging
from vscheduler.lib.config import Credentials as MyCredentials

class Capture_log(object):
    """
    Logging class to call in methods and capture event 
    logs into separate files for booking and pool.
    """
    def __init__(self, severity, location, event):
        self.formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
        self.severity = severity
        self.location = location
        self.event = event
    
    def extendable_logger(self, log_name, file_name, level=MyCredentials.log_level):
        handler = logging.FileHandler(file_name)
        handler.setFormatter(self.formatter) 
        specified_logger = logging.getLogger(log_name)
        specified_logger.setLevel(level)
        specified_logger.addHandler(handler)
        return specified_logger
    
    def log_pool(self):
        pool_logger = self.extendable_logger('pool_logs ' + self.location, 'pool.log')
        if self.severity == 'info':
            pool_logger.info(self.event)
        elif self.severity == 'debug':
            pool_logger.debug(self.event)
        elif self.severity == 'warning':
            pool_logger.warning(self.event)
        elif self.severity == 'error':
            pool_logger.error(self.event)
        elif self.severity == 'critical':
            pool_logger.critical(self.event)
    
    def log_booking(self):
        booking_logger = self.extendable_logger('booking_logs ' + self.location, 'booking.log')
        if self.severity == 'info':
            booking_logger.info(self.event)
        elif self.severity == 'debug':
            booking_logger.debug(self.event)
        elif self.severity == 'warning':
            booking_logger.warning(self.event)
        elif self.severity == 'error':
            booking_logger.error(self.event)
        elif self.severity == 'critical':
            booking_logger.critical(self.event)