# makes a node exception not to be called in allocation process, or gives exception status of all/specific node(s)
import multiprocessing, click
from vscheduler.log.log import CaptureLog
from vscheduler.lib import config
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.status import status_update as update_status
# from vscheduler.modules.reports.status import exception_add as add_exception
# from vscheduler.modules.reports.status import exception_remove as remove_exception
# from vscheduler.modules.reports.status import exception_status as status_exception

records = CaptureLog("exception", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, status, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.status = status
    
    def run(self):
        update_status (self.hostname, self.status)
        # if self.status == "down":
        #     add_exception (self.hostname)
        #     logger_win.info (f"< {self.hostname} > requested to be added to exception") if MyCredentials.windows_node_name in self.hostname else logger_unix.info (f"< {self.hostname} > requested to be added to exception")
        # elif self.status == "remove":    
        #     remove_exception (self.hostname)
        #     logger_win.info (f"< {self.hostname} > requested to be remved from exception") if MyCredentials.windows_node_name in self.hostname else logger_unix.info (f"< {self.hostname} > requested to be removed from exception")
        # elif self.status == "status":
        #     start = '2000-01-01' if not initiate.start else initiate.start
        #     end = MyBrackets.local_time if not initiate.end else initiate.end
        #     print (f"start: {start}")
        #     print (f"end: {end}")
        #     status_exception(self.hostname, start, end)
        #     logger_win.info (f"< {self.hostname} > queried for exception status") if MyCredentials.windows_node_name in self.hostname else logger_unix.info (f"< {self.hostname} > queried for exception status")

def main():
    # if not initiate.node:
    #     for i in range (MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
    #         node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
    #         if initiate.add:
    #             p = Process(i, "add", node)
    #         elif initiate.remove:
    #             p = Process(i, "remove", node)
    #         elif initiate.status:
    #             p = Process(i, "status", node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     for i in range (MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
    #         node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
    #         if initiate.add:
    #             p = Process(i, "add", node)
    #         elif initiate.remove:
    #             p = Process(i, "remove", node)
    #         elif initiate.status:
    #             p = Process(i, "status", node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     for i in range (MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
    #         node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
    #         if initiate.add:
    #             p = Process(i, "add", node)
    #         elif initiate.remove:
    #             p = Process(i, "remove", node)
    #         elif initiate.status:
    #             p = Process(i, "status", node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     for i in range (MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
    #         node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
    #         if initiate.add:
    #             p = Process(i, "add", node)
    #         elif initiate.remove:
    #             p = Process(i, "remove", node)
    #         elif initiate.status:
    #             p = Process(i, "status", node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    # else:
    #     if initiate.add:
    #         p = Process("", "add", initiate.node)
    #     elif initiate.remove:
    #         p = Process("", "remove", initiate.node)
    #     elif initiate.status:
    #         p = Process("", "status", initiate.node)
    #     p.start()       # Create a new process and invoke the Process.run() method
    #     p.join()        # Process.join() to wait for task completion
    if initiate.node:
        p = Process("", initiate.status, initiate.node)
        p.start()       # Create a new process and invoke the Process.run() method
        p.join()        # Process.join() to wait for task completion
    else:
        print ("Missed node in status command. For more than one node use range i.e. [n1,n2] <<-- this to be coded")
    
if __name__ == '__main__':
    main()