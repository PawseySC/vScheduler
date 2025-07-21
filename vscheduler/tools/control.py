import multiprocessing, argparse
from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.lib.verbose import verbose
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
# from vscheduler.modules.cluster.maintenance import activation as activate
# from vscheduler.modules.cluster.maintenance import deactivation as deactivate
# from vscheduler.modules.cluster.maintenance import activation_status as status_activation
from vscheduler.modules.guaca.maintenance import change_maint_status
from vscheduler.modules.reports.status import status_update as update_status

control_records = CaptureLog("control", __file__)
logger = control_records.log_agent("tools")
config = Config()

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
    """
    Makes a node exception not to be called in allocation process, or gives exception status of all/specific node(s)
    """
    parser = argparse.ArgumentParser(
        description="Apply mode to a partition or node: training, maintenance, up, down",
        usage="vcontrol operation mode [-n Node] [-p Partition] [--verbose] [--version]")
    parser.add_argument("operation", help="create, delete, set")
    parser.add_argument("mode", help="training, maintenance, up, down")
    parser.add_argument("-n", metavar="Node", help="node name")
    parser.add_argument("-p", metavar="Partition", help="partition name")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--version", action="version", version="vscheduler v" + config.get("version.v"))
    args = parser.parse_args()
    # print(args.u, args.n, args.verbose)
    
    if args.operation != "set":
        if args.p:
            change_maint_status(args.mode, args.p)
        elif args.n:
            print (f"vscontrol create/delete only works with parttiton. For node use vcontrol set -n {args.n} to modify the mode")    
    else:
        if not args.n:
            print ("Node name is required for vcontrol set operation. Use -n <node> to specify the node.")
            return
        else:
            if args.mode != "training":
                update_status (args.n, args.mode)
            else:
                print ("Training mode is not supported for nodes. Use vcontrol create/delete -p <partitione> to set training mode for a partition.")

    # if not initiate.node:
        # # print (initiate.mode, initiate.partition)
        # change_maint_status (initiate.mode, initiate.partition)

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
    # else:
        # if initiate.add:
        #     p = Process("", "add", initiate.node)
        # elif initiate.remove:
        #     p = Process("", "remove", initiate.node)
        # elif initiate.status:
        #     p = Process("", "status", initiate.node)
        # p.start()       # Create a new process and invoke the Process.run() method
        # p.join()        # Process.join() to wait for task completion
        # print ("Maintenance mode will be applied for all nodes; To exclude specific node, use vexcept")
    # p = Process("", initiate.status, initiate.node)
    # p.start()       # Create a new process and invoke the Process.run() method
    # p.join()        # Process.join() to wait for task completion
    
if __name__ == '__main__':
    main()