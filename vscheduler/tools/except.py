# allocates connection link to specific node of general pool in user's guacamole dashboard
import multiprocessing
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.exception import exception_update, exception_list


records = Capture_log("exception", __file__)
logger_exception = records.log_agent("exception")


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
        # time.sleep(1)
        # print (f"user: {self.username}") if MyPrintCondition.fprint else 0
        if self.mode == "list" or self.mode == "status":
            exception_list (self.username, self.start_date, self.end_date)
        elif self.mode == "activate" or self.mode == "deactivate":
            exception_update (self.username, self.mode, self.time)

def main():
    if not initiate.node:
        if initiate.mode == 'list':
            if initiate.user:
                print ("no username is needed when listing exceptions\nplease see help")
            else:
                p = Process("", "list", "", initiate.start, initiate.end)
                p.start()
                p.join()
        elif initiate.mode == 'status':
            if not initiate.user:
                print ("username is needed when querying exception status\nplease see help")
            else:
                p = Process(initiate.user, "status", "", initiate.start, initiate.end)
                p.start()
                p.join()
        elif initiate.mode == 'activate':
            if not initiate.user or not initiate.time:
                print ("vexcept activate requires username and time\nplease see help")
            else:
                p = Process(initiate.user, "activate", initiate.time, "", "")
                p.start()
                p.join()
                # [(Process(users, "activate"), Process(users, "activate").start(), Process(users, "activate").join()) for users in initiate.user]
        elif initiate.mode == 'deactivate':
            if not initiate.user:
                print ("vexcept deactivate requires username\nplease see help")
            else:
                p = Process(initiate.user, "deactivate", "", "", "")
                p.start()
                p.join()
                # [(Process(users, "deactivate"), Process(users, "deactivate").start(), Process(users, "deactivate").join()) for users in initiate.user]
    else:
        print ("vexcept doesn't require node\nplease see help")
        


if __name__ == '__main__':
    main()