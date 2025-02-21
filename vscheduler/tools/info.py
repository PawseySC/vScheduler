import multiprocessing, click, time
from vscheduler.log.log import CaptureLog
from tabulate import tabulate
from vscheduler.lib.config import Config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.information import print_info
from vscheduler.modules.reports.information import session

tools_records = CaptureLog("info", __file__)
logger = tools_records.log_agent("tools")


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
    
    def run(self):
        session (self.hostname)
        
def main():
    """
    vinfo script giving overview of all nodes' status
    """
    if initiate.session:
        print (initiate.session)
        if not initiate.node:
            if Config.config['partition']['windows']['booking']['status']or Config.config['partition']['windows']['general']['status']:
                if Config.config['partition']['windows']['booking']['status']:
                    for i in range (Config.config['partition']['windows']['booking']['range'][0], Config.config['partition']['windows']['booking']['range'][1]+1):
                        node = Config.config['partition']['windows']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['windows']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if Config.config['partition']['windows']['general']['status']:
                    for i in range (Config.config['partition']['windows']['general']['range'][0], Config.config['partition']['windows']['general']['range'][1]+1):
                        node = Config.config['partition']['windows']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['windows']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
            else:
                print ("There is no Windows partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
                logger.info ("There is no Windows partition; To enable it edit vscheduler confilg")
            if Config.config['partition']['linux']['booking']['status'] or Config.config['partition']['linux']['general']['status']:
                if Config.config['partition']['linux']['booking']['status']:
                    for i in range (Config.config['partition']['linux']['booking']['range'][0], Config.config['partition']['linux']['booking']['range'][1]+1):
                        node = Config.config['partition']['linux']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['linux']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if Config.config['partition']['linux']['general']['status']:
                    for i in range (Config.config['partition']['linux']['general']['range'][0], Config.config['partition']['linux']['general']['range'][1]+1):
                        node = Config.config['partition']['linux']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['linux']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
            else:
                print ("There is no Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
                logger.info ("There is no Linux partition; To enable it edit vscheduler confilg")    
        elif initiate.node:
            p = Process("", initiate.node)
            p.start()       # Create a new process and invoke the Process.run() method
            p.join()        # Process.join() to wait for task completion
    else:
        print_info()

if __name__ == '__main__':
    main()