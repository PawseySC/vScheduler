# vinfo script
import multiprocessing, click, time
from vscheduler.log.log import Capture_log
from tabulate import tabulate
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.information import print_info
from vscheduler.modules.reports.information import session

records = Capture_log("info", __file__)
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
            if MyCredentials.windows_booking or MyCredentials.windows_general:
                if MyCredentials.windows_booking:
                    for i in range (MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
                        node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if MyCredentials.windows_general:
                    for i in range (MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
                        node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
            else:
                print ("There is no Windows partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
                logger.info ("There is no Windows partition; To enable it edit vscheduler confilg")
            if MyCredentials.linux_booking or MyCredentials.linux_general:
                if MyCredentials.linux_booking:
                    for i in range (MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
                        node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
                        p = Process(i, node)
                        p.start()       # Create a new process and invoke the Process.run() method
                        p.join()        # Process.join() to wait for task completion
                if MyCredentials.linux_general:
                    for i in range (MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
                        node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
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