import multiprocessing, argparse
from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.lib.verbose import verbose
from vscheduler import __version__
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.who import who
#from vscheduler.modules.cluster.session import session
# from vscheduler.modules.cluster.logoff import logoff
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guaca_user_group import guacamole_user_group
from vscheduler.modules.guaca.check_group import check_group
from vscheduler.modules.guaca.update import update
from vscheduler.lib.ranger import parse_node_range

allocate_records = CaptureLog("allocate", __file__)
logger = allocate_records.log_agent("tools")
config = Config()


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username
    
    def run(self):
        """
        Allocates connection link to specific general pool node in user's guacamole dashboard
        """
        # time.sleep(1)
        print ("\n==>Process id: {}".format(self.id)) if verbose.mode and self.id else 0 # if MyPrintCondition.fprint and self.id else 0
        # if config.get("partition.windows.node") in self.hostname:
        #     logger_win.info ("==>Process id: {}".format(self.id)) if self.id else 0
        # elif config.get("partition.linux.node") in self.hostname:
        #     logger_unix.info ("==>Process id: {}".format(self.id)) if self.id else 0
        logger.info ("==>Process id: {}".format(self.id)) if self.id else 0

        users = who(self.hostname) if not self.username else [self.username]                        # retreives users logged in to the node
        print ("users=>", users)
        # logger_win.info (f"users=> {users}") if config.get("partition.windows.node") in self.hostname else logger_unix.info (f"users=> {users}")
        logger.info (f"users=> {users}")

        node_entity = entity(self.hostname)        
        node_user_group = guacamole_user_group(node_entity[0][0])
        group_check = check_group (node_user_group[0][0])
        # if group_check:
        #     pool_entity = entity(MyCredentials.pool)
        #     pool_group = guacamole_user_group(pool_entity[0][0])

        if users:
            for user in users:
                #length = session(self.hostname, user)
                user_entity = entity(user)  
                # if not group_check or group_check[0][0] != node_user_group[0][0]:                        # if user's connected to a node -> remove it from general poll & asigne it to that node connection group
                # pool_entity = entity(config.get("partition.windows.general.pool")) if config.get("partition.windows.node") in self.hostname else entity(config.get("partition.linux.general.pool"))
                pool_entity = entity(config.get("partition.windows.general.pool")) if config.get("partition.windows.node") in self.hostname else entity(config.get("partition.linux.general.pool"))
                pool_user_group = guacamole_user_group(pool_entity[0][0])
                update(user_entity[0][0], node_user_group[0][0], pool_user_group[0][0], "alloc", config.get("partition.windows.general.pool") if config.get("partition.windows.node") in self.hostname else config.get("partition.linux.general.pool"))                 
                #elif group_check and int(length) > (MyCredentials.general_pool_wall_time)*3600:    # if session's left open or longer than allowed -> kill the session & revert the user back into general pool 
                    #update(group_check[0][1], pool_group[0][0])
                    #logoff(user, self.hostname)
        # elif not users and group_check:                                                             # if user's not logged in -> revert it back to general pool
        #     update(group_check[0][1], pool_group[0][0])
        else:
            print (f"skipping < {self.hostname} > as no ones logged in (or due to broken ssh) and has no member in guacamole connection group") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            # logger_win.info (f"skipping < {self.hostname} > as no ones logged in (or due to broken ssh) and has no member in guacamole connection group") if Config.config['partition['windows']['node'] in self.hostname else logger_unix.info (f"skipping < {self.hostname} > as no ones logged in (or due to broken ssh) and has no member in guacamole connection group")
            logger.info (f"skipping < {self.hostname} > as no ones logged in (or due to broken ssh) and has no member in guacamole connection group")
            # think about this: user might have some light stuff open and e.g. waiting for mc to copy from object storage
            # or if they disconnected th session waiting for repeatative work to be done
            # above "else" will take this into consideration or remove the node link for that user? 
            # TO BE TESTED


def main():
    # import vscheduler.lib.verbose as verbose_flag
    # print(verbose_flag.VERBOSE)
    parser = argparse.ArgumentParser(
        description="Allocate a node to a user in the booking pool",
        usage="valloc [-u User] [-n Node] [--verbose] [--version]")
    parser.add_argument("-u", metavar="User", help="username")
    parser.add_argument("-n", metavar="Node", help="node name")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--version", action="version", version="vscheduler v" + __version__)
    args = parser.parse_args()
    print(args.u, args.n, args.verbose)
    if args.verbose:
        verbose.mode = True
        print("Verbose mode enabled") if verbose.mode else print("Verbose mode disabled")

    # if not initiate.node:
    if not args.n:
        if config.get("partition.windows.general.status") or config.get("partition.linux.general.status"):
            if config.get("partition.windows.general.status"):
                for i in range (config.get("partition.windows.general.range")[0], config.get("partition.windows.general.range")[1]+1):
                    node = config.get("partition.windows.node") + '0' + str(i) if i <= 9 else config.get("partition.windows.node") + str(i)
                    # p = Process(i, initiate.user, node)
                    p = Process(i, args.u, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if config.get("partition.linux.general.status"):
                for i in range (config.get("partition.linux.general.range")[0], config.get("partition.linux.general.range")[1]+1):
                    node = config.get("partition.linux.node") + '0' + str(i) if i <= 9 else config.get("partition.linux.node") + str(i)
                    # p = Process(i, initiate.user, node)
                    p = Process(i, args.u, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no general Windows and Linux partition; To enable it edit vscheduler confilg") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            logger.info ("There is no general Windows and Linux partition; To enable it edit vscheduler confilg")
            # logger_win.info ("There is no general Windows and Linux partition; To enable it edit vscheduler confilg")
            # logger_unix.info ("There is no general Windows and Linux partition; To enable it edit vscheduler confilg")
    else:
        nodes = parse_node_range(args.n)
        node_numbers = len(nodes)
        for i in range(node_numbers):
            # if ((config.get("partition.windows.node") in initiate.node and 
            #         int(initiate.node.removeprefix(config.get("partition.windows.node"))) in range(config.get("partition.windows.general.range")[0], config.get("partition.windows.general.range")[1]+1)) or 
            #         (config.get("partition.linux.node") in initiate.node and 
            #         int(initiate.node.removeprefix(config.get("partition.linux.node"))) in range(config.get("partition.linux.general.range")[0], config.get("partition.linux.general.range")[1]+1))):
            # if ((config.get("partition.windows.node") in args.n and 
            #     int(args.n.removeprefix(config.get("partition.windows.node"))) in range(config.get("partition.windows.general.range")[0], config.get("partition.windows.general.range")[1]+1)) or 
            #     (config.get("partition.linux.node") in args.n and 
            #     int(args.n.removeprefix(config.get("partition.linux.node"))) in range(config.get("partition.linux.general.range")[0], config.get("partition.linux.general.range")[1]+1))):
            if ((config.get("partition.windows.node") in nodes[i] and 
                int(nodes[i].removeprefix(config.get("partition.windows.node"))) in range(config.get("partition.windows.general.range")[0], config.get("partition.windows.general.range")[1]+1)) or 
                (config.get("partition.linux.node") in nodes[i] and 
                int(nodes[i].removeprefix(config.get("partition.linux.node"))) in range(config.get("partition.linux.general.range")[0], config.get("partition.linux.general.range")[1]+1))):
                # p = Process("", initiate.user, initiate.node)
                # p = Process("", args.u, args.n)
                p = Process(i, args.u, nodes[i])
                p.start()       # Create a new process and invoke the Process.run() method
                p.join()        # Process.join() to wait for task completion
            else:
                # print (f"< {initiate.node} > is not in general range") if MyPrintCondition.fprint else 0
                # print (f"< {args.n} > is not in general range") if verbose.mode else 0
                print (f"< {nodes[i]} > is not in general range") if verbose.mode else 0
                # logger_win.info (f"< {initiate.node} > is not in general range") if config.get("partition.windows.node") in initiate.node else logger_unix.info (f"< {initiate.node} > is not in general range")
                # logger.info (f"< {initiate.node} > is not in general range")
                # logger.info (f"< {args.n} > is not in general range")
                logger.info (f"< {nodes[i]} > is not in general range")

    #     for i in range (MyCredentials.range[0], MyCredentials.range[1]):
    #         node = MyCredentials.node_name + '0' + str(i) if i <= 9 else MyCredentials.node_name + str(i)
    #         p = Process(i, initiate.user, node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    # else:
    #     p = Process("", initiate.user, initiate.node)
    #     p.start()       # Create a new process and invoke the Process.run() method
    #     p.join()        # Process.join() to wait for task completion


# def register(subparsers):
#     parser = subparsers.add_parser("vmanage", help="Manages a bookable session")
#     parser.add_argument("user", help="User")
#     parser.add_argument("node", help="Node")
#     parser.add_argument("-v", type=int, required=True, help="Verbose")
#     parser.set_defaults(func=handle)

# def handle(args):
#     # This function is only called if args are valid
#     print(f"Checking session for {args.user} on {args.node}")

    
if __name__ == '__main__':
    main()