# allocates connection link to specific node of general pool in user's guacamole dashboard
import multiprocessing
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.administrator import admin_update, admin_list


records = Capture_log("admin", __file__)
logger_admin = records.log_agent("admin")


# Process class
class Process(multiprocessing.Process):
    def __init__(self, username, mode):
        super(Process, self).__init__()
        self.username = username
        self.mode = mode
    
    def run(self):
        # time.sleep(1)
        # print (f"user: {self.username}") if MyPrintCondition.fprint else 0
        if self.username == "list" or self.mode == "status":
            admin_list (self.username)
        elif self.mode == "activate" or self.mode == "deactivate":
            admin_update (self.username, self.mode)

def main():
    if not initiate.node:
        if initiate.list:
            if initiate.user:
                print ("no username is needed when listing admins\nplease see help")
            else:
                p = Process("", "list")
                p.start()
                p.join()
        elif initiate.stat:
            if not initiate.user:
                print ("username is needed when querying admin status\nplease see help")
            else:
                p = Process(initiate.user, "status")
                p.start()
                p.join()
        elif initiate.activate:
            if not initiate.user:
                print ("vadmin activate requires username\nplease see help")
            else:
                p = Process(initiate.user, "activate")
                p.start()
                p.join()
                # [(Process(users, "activate"), Process(users, "activate").start(), Process(users, "activate").join()) for users in initiate.user]
        elif initiate.deactivate:
            if not initiate.user:
                print ("vadmin deactivate requires username\nplease see help")
            else:
                p = Process(initiate.user, "deactivate")
                p.start()
                p.join()
                # [(Process(users, "deactivate"), Process(users, "deactivate").start(), Process(users, "deactivate").join()) for users in initiate.user]
    else:
        print ("vadmin doesn't require node\nplease see help")
        


if __name__ == '__main__':
    main()