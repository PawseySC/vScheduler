# quota script
import multiprocessing, click, time
from vscheduler.log.log import Capture_log
from tabulate import tabulate
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.cluster.who import who

records = Capture_log("booking/pool", __file__)
logger = records.log_agent()

# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username
        self.found = False

    def run(self):
        # time.sleep(1)
        print ("\n==>> Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        logger.info ("\n==>Process id: {}".format(self.id)) if self.id else 0
        users = who(self.hostname) if not self.username else [self.username]                        # retreives node logged in users
        sentence = []
        if users:
            if not self.username:
                for user in users:
                    sentence.insert(len(sentence), [user])
                print ("\n", tabulate(sentence, headers=[self.hostname + " logged in users"])) if MyPrintCondition.fprint else 0
                logger.info ("\n" + tabulate(sentence, headers=[self.hostname + " logged in users"]))
            
            # answer = input("Do you want above sessions to be killed? (Y/N)") if not self.username else input("Do you want to kill <", self.username,"> sessions on < ", self.hostname,"> ? (Y/N)")
            # print ("answer", answer)
            # if answer == "Y" or "y":
            for user in users:
                logoff(user, self.hostname)
            # else:
                # print ("skipped", self.hostname, "sessions")
        else:
            print (f"no one is logged in < {self.hostname} > , skipping") if MyPrintCondition.fprint else 0
            logger.info (f"no one is logged in < {self.hostname} > , skipping")


def main():
    if not initiate.node:
        if MyCredentials.windows_booking or MyCredentials.windows_general:
            if MyCredentials.windows_booking:
                for i in range (MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
                    node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if MyCredentials.windows_general:
                for i in range (MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
                    node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no Windows partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            logger.info ("There is no Windows partition; To enable it edit vscheduler confilg")
        if MyCredentials.linux_booking or MyCredentials.linux_general:
            if MyCredentials.linux_booking:
                for i in range (MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
                    node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if MyCredentials.linux_general:
                for i in range (MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
                    node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            logger.info ("There is no Linux partition; To enable it edit vscheduler confilg")
    else:
        p = Process("", initiate.user, initiate.node)
        p.start()       # Create a new process and invoke the Process.run() method
        p.join()        # Process.join() to wait for task completion


if __name__ == '__main__':
    main()