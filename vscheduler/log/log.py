import logging
from vscheduler.lib import config

class CaptureLog(object):
    """
    Logging class to be called in methods capturing event logs into dedicated log file
    """
    def __init__(self, flag, location):
        self.formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
        self.flag = flag
        self.location = location
    
    def extendable_logger(self, log_name, file_name, level = config.log['level']):
        handler = logging.FileHandler(file_name)
        handler.setFormatter(self.formatter) 
        specified_logger = logging.getLogger(log_name)
        specified_logger.setLevel(level)
        specified_logger.addHandler(handler)
        return specified_logger
    
    def log_agent(self, partition):
        # agent_logger = self.extendable_logger(self.flag + " " + self.location, f'/home/ubuntu/visualisation_scheduler/vscheduler/log/{MyCredentials.report_windows_table}-log.log') if partition == "windows" else self.extendable_logger(self.flag + " " + self.location, f'/home/ubuntu/visualisation_scheduler/vscheduler/log/{MyCredentials.report_linux_table}-log.log')
        agent_logger = self.extendable_logger(f"{self.flag} {self.location}", f'/home/ubuntu/visualisation_scheduler/vscheduler/log/{partition}.log')
        return agent_logger