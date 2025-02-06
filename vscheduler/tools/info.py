# vinfo script
import multiprocessing, click, time
from vscheduler.log.log import CaptureLog
from tabulate import tabulate
from vscheduler.lib import config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.information import print_info
from vscheduler.modules.reports.information import session

records = CaptureLog("info", __file__)
logger = records.log_agent("info")


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
    
    def run(self):
        session (self.hostname)
        
def main():
    if initiate.session:
        print (initiate.session)
        if not initiate.node:
            if config.partition['windows']['booking']['status']or config.partition['windows']['general']['status']:
                if config.partition['windows']['booking']['status']:
                    for i in range (config.partition['windows']['booking']['range'][0], config.partition['windows']['booking']['range'][1]+1):
                        node = config.partition['windows']['node'] + '0' + str(i) if i <= 9 else config.partition['windows']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if config.partition['windows']['general']['status']:
                    for i in range (config.partition['windows']['general']['range'][0], config.partition['windows']['general']['range'][1]+1):
                        node = config.partition['windows']['node'] + '0' + str(i) if i <= 9 else config.partition['windows']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
            else:
                print ("There is no Windows partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
                logger.info ("There is no Windows partition; To enable it edit vscheduler confilg")
            if config.partition['linux']['booking']['status'] or config.partition['linux']['general']['status']:
                if config.partition['linux']['booking']['status']:
                    for i in range (config.partition['linux']['booking']['range'][0], config.partition['linux']['booking']['range'][1]+1):
                        node = config.partition['linux']['node'] + '0' + str(i) if i <= 9 else config.partition['linux']['node'] + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if config.partition['linux']['general']['status']:
                    for i in range (config.partition['linux']['general']['range'][0], config.partition['linux']['general']['range'][1]+1):
                        node = config.partition['linux']['node'] + '0' + str(i) if i <= 9 else config.partition['linux']['node'] + str(i)
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