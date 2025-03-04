import os, logging
import logging.handlers as handlers
from vscheduler.lib.config import Config
config = Config()

class CaptureLog(object):
    """
    Logging class facilitates methods to capture event logs into dedicated log file
    """
    def __init__(self, flag, location):
        self.formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
        self.flag = flag
        self.location = location
    
    def extendable_logger(self, log_name, file_name, level = config.get("log.level")):
        # handler = logging.FileHandler(file_name)                                                              # contineous logging in same file
        handler = handlers.TimedRotatingFileHandler(file_name, when="d", interval=1)    # , backupCount=30      # logs into separate files for configured time intervals
        handler.setFormatter(self.formatter) 
        specified_logger = logging.getLogger(log_name)
        specified_logger.setLevel(level)
        specified_logger.addHandler(handler)
        return specified_logger
    
    def log_agent(self, partition):
        log_file = os.path.join(os.path.dirname(__file__), f'{partition}.log')
        agent_logger = self.extendable_logger(f"{self.flag} {self.location}", f'{log_file}')
        return agent_logger