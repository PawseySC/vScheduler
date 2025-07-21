import multiprocessing, argparse
from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.lib.verbose import verbose
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.exception import exception_update, exception_list

exception_records = CaptureLog("exception", __file__)
logger = exception_records.log_agent("tools")
config = Config()


# Process class
class Process(multiprocessing.Process):
    def __init__(self, username, mode, time, start, end):
        super(Process, self).__init__()
        self.username = username
        self.mode = mode
        self.start_date = start
        self.end_date = end
        self.time = time
    
    def run(self):
        """
        Allocates connection link to specific node of general pool in user's guacamole dashboard
        """
        # time.sleep(1)
        # print (f"user: {self.username}") if MyPrintCondition.fprint else 0
        if self.mode == "list" or self.mode == "status":
            exception_list (self.username, self.start_date, self.end_date)
        elif self.mode == "activate" or self.mode == "deactivate":
            exception_update (self.username, self.mode, self.time)

def main():
    parser = argparse.ArgumentParser(
        description="Apply or query user status for wall time: list , status, activate, deactivate",
        usage="vexcept list/status/activate/deactivate [-u User] [--verbose] [--version]")
    parser.add_argument("operation", help="list, status, activate, deactivate")
    parser.add_argument("-u", metavar="User", help="username")
    parser.add_argument("-t", metavar="Time", help="time in integer in hours")
    parser.add_argument("-d1", metavar="Start date", help="YYYY-MM-DD format")
    parser.add_argument("-d2", metavar="End date", help="YYYY-MM-DD format")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--version", action="version", version="vscheduler v" + config.get("version.v"))
    args = parser.parse_args()
    if args.verbose:
        verbose.mode = True
        print("Verbose mode enabled") if verbose.mode else print("Verbose mode disabled")

    # if not args.u:
    # if not initiate.node:
    if args.operation == "list":
    # if initiate.mode == 'list':
        if args.u:
        # if initiate.user:
            print ("no username is needed when listing exceptions\nplease see help")
        else:
            p = Process("", "list", "", args.d1, args.d2)
            # p = Process("", "list", "", initiate.start, initiate.end)
            p.start()
            p.join()
    elif args.operation == "status":
    # elif initiate.mode == 'status':
        if not args.u:
        # if not initiate.user:
            print ("username is needed when querying exception status\nplease see help")
        else:
            p = Process(args.u, "status", "", args.d1, args.d2)
            # p = Process(initiate.user, "status", "", initiate.start, initiate.end)
            p.start()
            p.join()
    elif args.operation == "activate":
    # elif initiate.mode == 'activate':
        if not args.u or not args.t:
        # if not initiate.user or not initiate.time:
            print ("vexcept activate requires username and time\nplease see help")
        else:
            p = Process(args.u, "activate", args.t, "", "")
            # p = Process(initiate.user, "activate", initiate.time, "", "")
            p.start()
            p.join()
            # [(Process(users, "activate"), Process(users, "activate").start(), Process(users, "activate").join()) for users in initiate.user]
    elif args.operation == "deactivate":
    # elif initiate.mode == 'deactivate':
        if not args.u:
        # if not initiate.user:
            print ("vexcept deactivate requires username\nplease see help")
        else:
            p = Process(args.u, "deactivate", "", "", "")
            # p = Process(initiate.user, "deactivate", "", "", "")
            p.start()
            p.join()
            # [(Process(users, "deactivate"), Process(users, "deactivate").start(), Process(users, "deactivate").join()) for users in initiate.user]
    # else:
    #     print ("vexcept doesn't require node\nplease see help")
        


if __name__ == '__main__':
    main()