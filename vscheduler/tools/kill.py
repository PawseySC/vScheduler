import multiprocessing, click, time
from vscheduler.log.log import CaptureLog
from tabulate import tabulate
from vscheduler.lib.config import Config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.cluster.who import who

kill_records = CaptureLog("kill", __file__)
logger = kill_records.log_agent("tools")
config = Config()


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username
        self.found = False

    def run(self):
        """
        Sesssion killing script logging out users
        """
        # time.sleep(1)
        print ("\n==>> Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        # if config.get("partition.windows.node") in self.hostname:
        #     logger_win.info ("==>Process id: {}".format(self.id)) if self.id else 0
        # elif config.get("partition.linux.node") in self.hostname:
        #     logger_unix.info ("==>Process id: {}".format(self.id)) if self.id else 0
        logger.info ("==>Process id: {}".format(self.id)) if self.id else 0
        users = who(self.hostname) if not self.username else [self.username]                        # retreives node logged in users
        sentence = []
        if users:
            if not self.username:
                for user in users:
                    sentence.insert(len(sentence), [user])
                print ("\n" + tabulate(sentence, headers=[self.hostname + " logged in users"])) if MyPrintCondition.fprint else 0
                # logger_win.info ("\n" + tabulate(sentence, headers=[self.hostname + " logged in users"])) if config.get("partition.windows.node") in self.hostname else logger_unix.info ("\n" + tabulate(sentence, headers=[self.hostname + " logged in users"]))
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
            # logger_win.info (f"no one is logged in < {self.hostname} > , skipping") if config.get("partition.windows.node") in self.hostname else logger_unix.info (f"no one is logged in < {self.hostname} > , skipping")
            logger.info (f"no one is logged in < {self.hostname} > , skipping")


def main():
    if not initiate.node:
        if config.get("partition.windows.booking.status") or config.get("partition.windows.general.status"):
            if config.get("partition.windows.booking.status"):
                for i in range (config.get("partition.windows.booking.range")[0], config.get("partition.windows.booking.range")[1]+1):
                    node = config.get("partition.windows.node") + '0' + str(i) if i <= 9 else config.get("partition.windows.node") + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if config.get("partition.windows.general.status"):
                for i in range (config.get("partition.windows.general.range")[0], config.get("partition.windows.general.range")[1]+1):
                    node = config.get("partition.windows.node") + '0' + str(i) if i <= 9 else config.get("partition.windows.node") + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no Windows partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            # logger_win.info ("There is no Windows partition; To enable it edit vscheduler confilg")
            logger.info ("There is no Windows partition; To enable it edit vscheduler confilg")
        if config.get("partition.linux.booking.status") or config.get("partition.linux.general.status"):
            if config.get("partition.linux.booking.status"):
                for i in range (config.get("partition.linux.booking.range")[0], config.get("partition.linux.booking.range")[1]+1):
                    node = config.get("partition.linux.node") + '0' + str(i) if i <= 9 else config.get("partition.linux.node") + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if config.get("partition.linux.general.status"):
                for i in range (config.get("partition.linux.general.range")[0], config.get("partition.linux.general.range")[1]+1):
                    node = config.get("partition.linux.node") + '0' + str(i) if i <= 9 else config.get("partition.linux.node") + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            # logger_unix.info ("There is no Linux partition; To enable it edit vscheduler confilg")
            logger.info ("There is no Linux partition; To enable it edit vscheduler confilg")
    else:
        p = Process("", initiate.user, initiate.node)
        p.start()       # Create a new process and invoke the Process.run() method
        p.join()        # Process.join() to wait for task completion


if __name__ == '__main__':
    main()