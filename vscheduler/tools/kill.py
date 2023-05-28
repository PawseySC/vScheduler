# quota script
import multiprocessing, click, time
from tabulate import tabulate
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.logoff import logoff
from vscheduler.modules.cluster.who import who


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
        users = who(self.hostname) if not self.username else [self.username]                        # retreives node logged in users
        sentence = []
        if users:
            if not self.username:
                for user in users:
                    sentence.insert(len(sentence), [user])
                print ("\n", tabulate(sentence, headers=[self.hostname + ' logged in users']))
            
            # answer = input("Do you want above sessions to be killed? (Y/N)") if not self.username else input("Do you want to kill <", self.username,"> sessions on < ", self.hostname,"> ? (Y/N)")
            # print ("answer", answer)
            # if answer == "Y" or "y":
            for user in users:
                logoff(user, self.hostname)
            # else:
                # print ("skipped", self.hostname, "sessions")
        else:
            print ("no one is logged in <", self.hostname, "> , skipping")


def loop_a(go):
    while True:
        # run forever and print out the msg if the flag is set
        time.sleep(1)
        if go.value:
            print("a")

def main():
    if not initiate.node:
        for i in range (MyCredentials.range[0], MyCredentials.range[1]):
            node = MyCredentials.node_name + '0' + str(i) if i <= 9 else MyCredentials.node_name + str(i)
            p = Process(i, initiate.user, node)
            p.start()       # Create a new process and invoke the Process.run() method
            p.join()        # Process.join() to wait for task completion
    else:
        p = Process("", initiate.user, initiate.node)
        p.start()       # Create a new process and invoke the Process.run() method
        p.join()        # Process.join() to wait for task completion


if __name__ == '__main__':
    main()