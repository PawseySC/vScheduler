import multiprocessing, time
from vscheduler.log.log import CaptureLog
from tabulate import tabulate
from vscheduler.lib.config import Config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.information import print_info
from vscheduler.modules.reports.information import session

tools_records = CaptureLog("info", __file__)
logger = tools_records.log_agent("tools")
config = Config()


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
            if config.get("partition.windows.booking.status") or config.get("partition.windows.general.status"):
                if config.get("partition.windows.booking.status"):
                    for i in range (config.get("partition.windows.booking.range")[0], config.get("partition.windows.booking.range")[1]+1):
                        node = config.get("partition.windows.node") + '0' + str(i) if i <= 9 else config.get("partition.windows.node") + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if config.get("partition.windows.general.status"):
                    for i in range (config.get("partition.windows.general.range")[0], config.get("partition.windows.general.range")[1]+1):
                        node = config.get("partition.windows.node") + '0' + str(i) if i <= 9 else config.get("partition.windows.node") + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
            else:
                print ("There is no Windows partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
                logger.info ("There is no Windows partition; To enable it edit vscheduler confilg")
            if config.get("partition.linux.booking.status") or config.get("partition.linux.general.status"):
                if config.get("partition.linux.booking.status"):
                    for i in range (config.get("partition.linux.booking.range")[0], config.get("partition.linux.booking.range")[1]+1):
                        node = config.get("partition.linux.node") + '0' + str(i) if i <= 9 else config.get("partition.linux.node") + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if config.get("partition.linux.general.status"):
                    for i in range (config.get("partition.linux.general.range")[0], config.get("partition.linux.general.range")[1]+1):
                        node = config.get("partition.linux.node") + '0' + str(i) if i <= 9 else config.get("partition.linux.node") + str(i)
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