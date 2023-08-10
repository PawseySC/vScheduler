# allocates connection link to specific node of general pool in user's guacamole dashboard
import multiprocessing, click
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.who import who
#from vscheduler.modules.cluster.session import session
# from vscheduler.modules.cluster.logoff import logoff
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guaca_user_group import guacamole_user_group
from vscheduler.modules.guaca.check_group import check_group
from vscheduler.modules.guaca.update import update

records = Capture_log("booking/pool", __file__)
logger = records.log_agent()

# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username
    
    def run(self):
        # time.sleep(1)
        print ("\n==>Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        logger.info ("\n==>Process id: {}".format(self.id)) if self.id else 0

        users = who(self.hostname) if not self.username else [self.username]                        # retreives users logged in to the node
        print ("users=>", users)
        logger.info ("users=>", users)

        node_entity = entity(self.hostname)        
        node_group = guacamole_user_group(node_entity[0][0])
        group_check = check_group (node_group[0][0])
        if group_check:
            pool_entity = entity(MyCredentials.pool)
            pool_group = guacamole_user_group(pool_entity[0][0])

        if users:
            for user in users:
                #length = session(self.hostname, user)
                user_entity = entity(user)  
                # if not group_check or group_check[0][0] != node_group[0][0]:                        # if user's connected to a node -> remove it from general poll & asigne it to that node connection group
                update(user_entity[0][0], node_group[0][0])                 
                #elif group_check and int(length) > (MyCredentials.general_pool_wall_time)*3600:    # if session's left open or longer than allowed -> kill the session & revert the user back into general pool 
                    #update(group_check[0][1], pool_group[0][0])
                    #logoff(user, self.hostname)
        # elif not users and group_check:                                                             # if user's not logged in -> revert it back to general pool
        #     update(group_check[0][1], pool_group[0][0])
        else:
            print (f"skipping < {self.hostname} > as no ones logged in (or due to broken ssh) and has no member in guacamole connection group") if MyPrintCondition.fprint else 0
            logger.info (f"skipping < {self.hostname} > as no ones logged in (or due to broken ssh) and has no member in guacamole connection group")
            # think about this: user might have some light stuff open and e.g. waiting for mc to copy from object storage
            # or if they disconnected th session waiting for repeatative work to be done
            # above "else" will take this into consideration or remove the node link for that user? 
            # TO BE TESTED


def main():
    if not initiate.node:
        if MyCredentials.windows_general or MyCredentials.linux_general:
            if MyCredentials.windows_general:
                for i in range (MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
                    node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
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
            print ("There is no general Windows or Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            logger.info ("There is no general Windows or Linux partition; To enable it edit vscheduler confilg")
    else:
        if ((MyCredentials.windows_node_name in initiate.node and 
                int(initiate.node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)) or 
                (MyCredentials.linux_node_name in initiate.node and 
                int(initiate.node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1))):
            p = Process("", initiate.user, initiate.node)
            p.start()       # Create a new process and invoke the Process.run() method
            p.join()        # Process.join() to wait for task completion
        else:
            print (f"< {initiate.node} > is not in general range") if MyPrintCondition.fprint else 0
            logger.info (f"< {initiate.node} > is not in general range")

    #     for i in range (MyCredentials.range[0], MyCredentials.range[1]):
    #         node = MyCredentials.node_name + '0' + str(i) if i <= 9 else MyCredentials.node_name + str(i)
    #         p = Process(i, initiate.user, node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    # else:
    #     p = Process("", initiate.user, initiate.node)
    #     p.start()       # Create a new process and invoke the Process.run() method
    #     p.join()        # Process.join() to wait for task completion



if __name__ == '__main__':
    main()
