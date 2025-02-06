# makes a node exception not to be called in allocation process, or gives exception status of all/specific node(s)
import multiprocessing, click
from vscheduler.log.log import CaptureLog
from vscheduler.lib import config
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
# from vscheduler.modules.cluster.maintenance import activation as activate
# from vscheduler.modules.cluster.maintenance import deactivation as deactivate
# from vscheduler.modules.cluster.maintenance import activation_status as status_activation
from vscheduler.modules.guaca.maintenance import change_maint_status

records = CaptureLog("control", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")

# Process class
# class Process(multiprocessing.Process):
#     def __init__(self, id, status, node):
#         super(Process, self).__init__()
#         self.id = id
#         self.hostname = node
#         self.status = status
    
#     def run(self):
#         if self.status == "activate":
#             activate (self.hostname)
#         elif self.status == "deactivate":    
#             deactivate (self.hostname)
#         elif self.status == "status":
#             start = '2000-01-01' if not initiate.start else initiate.start
#             end = MyBrackets.local_time if not initiate.end else initiate.end
#             print (f"start: {start}")
#             print (f"end: {end}")
#             status_activation (self.hostname, start, end)

def main():
    if not initiate.node:
        print (initiate.mode, initiate.partition)
        change_maint_status (initiate.mode, initiate.partition)
        # for i in range (MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
        #     node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
        #     if initiate.status == 'activate':
        #         p = Process(i, "activate", node)
        #     elif initiate.status == 'deactivate':
        #         p = Process(i, "deactivate", node)
        #     elif initiate.status == 'status':
        #         p = Process(i, "status", node)
        #     p.start()       # Create a new process and invoke the Process.run() method
        #     p.join()        # Process.join() to wait for task completion
        # for i in range (MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
        #     node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
        #     if initiate.status == 'activate':
        #         p = Process(i, "activate", node)
        #     elif initiate.status == 'deactivate':
        #         p = Process(i, "deactivate", node)
        #     elif initiate.status == 'status':
        #         p = Process(i, "status", node)
        #     p.start()       # Create a new process and invoke the Process.run() method
        #     p.join()        # Process.join() to wait for task completion
        # for i in range (MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
        #     node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
        #     if initiate.status == 'activate':
        #         p = Process(i, "activate", node)
        #     elif initiate.status == 'deactivate':
        #         p = Process(i, "deactivate", node)
        #     elif initiate.status == 'status':
        #         p = Process(i, "status", node)
        #     p.start()       # Create a new process and invoke the Process.run() method
        #     p.join()        # Process.join() to wait for task completion
        # for i in range (MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
        #     node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
        #     if initiate.status == 'activate':
        #         p = Process(i, "activate", node)
        #     elif initiate.status == 'deactivate':
        #         p = Process(i, "deactivate", node)
        #     elif initiate.status == 'status':
        #         p = Process(i, "status", node)
        #     p.start()       # Create a new process and invoke the Process.run() method
        #     p.join()        # Process.join() to wait for task completion
    else:
        # if initiate.add:
        #     p = Process("", "add", initiate.node)
        # elif initiate.remove:
        #     p = Process("", "remove", initiate.node)
        # elif initiate.status:
        #     p = Process("", "status", initiate.node)
        # p.start()       # Create a new process and invoke the Process.run() method
        # p.join()        # Process.join() to wait for task completion
        print ("Maintenance mode will be applied for all nodes; To exclude specific node, use vexcept")
    # p = Process("", initiate.status, initiate.node)
    # p.start()       # Create a new process and invoke the Process.run() method
    # p.join()        # Process.join() to wait for task completion
    
if __name__ == '__main__':
    main()