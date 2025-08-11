import multiprocessing, argparse
from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.lib.verbose import verbose
from vscheduler import __version__
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.timer import Brackets
from vscheduler.modules.booked.host import host_by_name                            # retreives host identification in booked
from vscheduler.modules.booked.resource import resource_reservations               # retreives series id of each resource
from vscheduler.modules.booked.reservation import user_reservations_by_user_id     # retreives reservation instance id of bookings for each user
from vscheduler.modules.cluster.who import who                                     # who's logged in each node
from vscheduler.modules.booked.user import user_details_by_username                # retreives user identification in booked
from vscheduler.modules.booked.instances import reservation_instances              # retreives reservation instance id, series id, and timeline of bookings for determined time bracket
from vscheduler.modules.booked.deleted import deleted                              # retreives status id of each reservation instances
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.lib.ranger import parse_node_range

booking_records = CaptureLog("booked", __file__)
logger = booking_records.log_agent("tools")
config = Config()


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username
        self.found = False
        self.del_found = False

    def run(self):
        """
        Management script for bookable partition
        """
        user = ""
        # time.sleep(1)
        # print ("\n==>> Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        print ("\n==>> Process id: {}".format(self.id)) if verbose.mode and self.id else 0
        logger.info ("==>Process id: {}".format(self.id)) if self.id else 0

        resource_id = host_by_name(self.hostname)                                                   # retreives node resource id
        series_ids = resource_reservations(resource_id[0][0]) if resource_id else quit()  # NO BOOKING AT ALL               # retreives node series ids
        users = who(self.hostname) if not self.username else [self.username]                        # retreives node logged in users
        print (f"\nusers logged in or asked to be checked in < {self.hostname} >: {users}")  if verbose.mode else 0 #if MyPrintCondition.fprint else 0
        logger.info (f"\nusers logged in or asked to be checked in < {self.hostname} >: {users}")
        instances = reservation_instances(Brackets.start_bracket, Brackets.end_bracket)         # retreives booking records within time brackets

        if users:
            for user in users:
                self.found = False
                self.del_found = False
                print (f"\n--> user: {user}") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                logger.info (f"\n--> user: {user}")

                user_identity = user_details_by_username(user)                                      # retreives user identification
                if user_identity:
                    reservations = user_reservations_by_user_id(user_identity[0][0])                # retreives user booking records
                else: 
                    print (f"user < {user} > does not exist in booked db") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                    logger.info (f"user < {user} > does not exist in booked db")
                    logoff(user, self.hostname)
                    continue    
                # print (f"reservations for", user, reservations)
                if instances:
                    for instance in instances:
                        print (f"instance: {instance}") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                        logger.info (f"instance: {instance}")
                        print (f"instance[3]: {instance[3]}") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                        logger.info (f"instance[3]: {instance[3]}")
                        if instance[1] <= Brackets.utc_now and instance[2] >= Brackets.utc_now:         # if the booking is current
                            print ("booking for the current time") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                            logger.info ("booking for the current time")
                            if not any(instance[3] in x for x in series_ids):
                                print (f"none of reservation instances records matches booking(s) made for < {self.hostname} >") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                                logger.info (f"none of reservation instances records matches booking(s) made for < {self.hostname} >")
                                exit
                            else:
                                for series_id in series_ids:
                                    print (f"series_id[0]: {series_id[0]}") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                                    logger.info (f"series_id[0]: {series_id[0]}")
                                    if series_id[0] == instance[3]:
                                        if not any(instance[0] in x for x in reservations):
                                            print (f"none of records matches booking made by < {user} >") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                                            logger.info (f"none of records matches booking made by < {user} >")
                                        else:
                                            for reservation in reservations:
                                                print (f"reservation: {reservation}") if verbose.mode else 0 #if MyPrintCondition.fprint else 0
                                                logger.info (f"reservation: {reservation}")
                                                print (f"reservation[0]: {reservation[0]}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                                                logger.info (f"reservation[0]: {reservation[0]}")
                                                print (f"instance[0]: {instance[0]}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                                                logger.info (f"instance[0]: {instance[0]}")
                                                if reservation[0] == instance[0]:
                                                    if deleted(instance[3])[0][1] != 2:     # checks if booking is deleted
                                                        # if reservation[1] == user_identity[0]:
                                                        # **** add a condition here to make sure booking is for now ****
                                                        self.found = True
                                                        print ("all good") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                                                        logger.info ("all good")
                                                        break
                                                    else:
                                                        self.del_found = True
                                                        print ("deleted record") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                                                        logger.info ("deleted record")
                                                else:
                                                    print (f"booking record not for < {user} >") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                                                    logger.info (f"booking record not for < {user} >")
                                    else:
                                        print (f"record of < {self.hostname} > does not match this booking") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                                        logger.info (f"record of < {self.hostname} > does not match this booking")
                        else:
                            print ("booking not for the current time") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                            logger.info ("booking not for the current time")
                else:
                    print (f"no current booking for < {self.hostname} > in the time bracket set in the config - skipping and killing all sessions") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                    logger.info (f"no current booking for < {self.hostname} > in the time bracket set in the config - skipping and killing all sessions")
                    logoff(user, self.hostname)
                    continue
                if self.found == True:
                    print (f"matched the booking for < {user} > - session on < {self.hostname} > is valid") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                    logger.info (f"matched the booking for < {user} > - session on < {self.hostname} > is valid")
                else:
                    if not self.del_found:
                        print (f"no match found for < {user} > on < {self.hostname} > - session will be killed") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                        logger.info (f"no match found for < {user} > on < {self.hostname} > - session will be killed")
                    else:
                        print (f"booking for < {user} > on < {self.hostname} > has been deleted - session will be killed") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
                        logger.info (f"booking for < {user} > on < {self.hostname} > has been deleted - session will be killed")
                    logoff(user, self.hostname)       
        else:
            print (f"no one is using < {self.hostname} > - skipping") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            logger.info (f"no one is using < {self.hostname} > - skipping")


def main():
    parser = argparse.ArgumentParser(
        description="Manage bookable sessions",
        usage="vmanage [-u User] [-n Node] [--verbose] [--version]")
    parser.add_argument("-u", metavar="User", help="username")
    parser.add_argument("-n", metavar="Node", help="node name")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--version", action="version", version="vscheduler v" + __version__)
    args = parser.parse_args()
    print(args.u, args.n, args.verbose)
    if args.verbose:
        verbose.mode = True
        print("Verbose mode enabled") if verbose.mode else print("Verbose mode disabled")
        # verbose_flag.VERBOSE = args.verbose  # Set global verbose flag
        # config.set("verbose.status", True)
        # print("Verbose mode enabled", config.get("verbose.status"))
        # print("Verbose mode enabled", verbose_flag.VERBOSE)
    # from vscheduler.modules.booked.host import host_by_name
    Brackets.what_time(Brackets.utc_now, Brackets.local_time, Brackets.start_bracket, Brackets.end_bracket)
    # if not initiate.node:
    if not args.n:
        # for i in range (MyCredentials.range[0], MyCredentials.range[1]):
        #     node = MyCredentials.node_name + '0' + str(i) if i <= 9 else MyCredentials.node_name + str(i)
        #     p = Process(i, initiate.user, node)
        #     p.start()       # Create a new process and invoke the Process.run() method
        #     p.join()        # Process.join() to wait for task completion
        if config.get("partition.windows.booking.status") or config.get("partition.linux.booking.status") :
            if config.get("partition.windows.booking.status") :
                for i in range (config.get("partition.windows.booking.range")[0], config.get("partition.windows.booking.range")[1]+1):
                    node = config.get("partition.windows.node") + '0' + str(i) if i <= 9 else config.get("partition.windows.node") + str(i)
                    # p = Process(i, initiate.user, node)
                    p = Process(i, args.u, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if config.get("partition.linux.booking.status") :
                for i in range (config.get("partition.linux.booking.range")[0], config.get("partition.linux.booking.range")[1]+1):
                    node = config.get("partition.linux.node") + '0' + str(i) if i <= 9 else config.get("partition.linux.node") + str(i)
                    # p = Process(i, initiate.user, node)
                    p = Process(i, args.u, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            # print ("There is no bookable Windows or Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            print ("There is no bookable Windows or Linux partition; To enable it edit vscheduler confilg") if verbose.mode else 0
            logger.info ("There is no bookable Windows or Linux partition; To enable it edit vscheduler confilg")
    else:
        nodes = parse_node_range(args.n)
        node_numbers = len(nodes)
        for i in node_numbers:
            # if (config.get("partition.windows.node") in initiate.node and 
            #         int(initiate.node.removeprefix(config.get("partition.windows.node"))) in range(config.get("partition.windows.booking.range")[0], config.get("partition.windows.booking.range")[1]+1) or 
            #         (config.get("partition.linux.node") in initiate.node and 
            #         int(initiate.node.removeprefix(config.get("partition.linux.node"))) in range(config.get("partition.linux.booking.range")[0], config.get("partition.linux.booking.range")[1]+1))):
            # if (config.get("partition.windows.node") in args.n and 
            #     int(args.n.removeprefix(config.get("partition.windows.node"))) in range(config.get("partition.windows.booking.range")[0], config.get("partition.windows.booking.range")[1]+1) or 
            #     (config.get("partition.linux.node") in args.n and 
            #     int(args.n.removeprefix(config.get("partition.linux.node"))) in range(config.get("partition.linux.booking.range")[0], config.get("partition.linux.booking.range")[1]+1))):
            if (config.get("partition.windows.node") in nodes[i] and 
                int(nodes[i].removeprefix(config.get("partition.windows.node"))) in range(config.get("partition.windows.booking.range")[0], config.get("partition.windows.booking.range")[1]+1) or 
                (config.get("partition.linux.node") in nodes[i] and 
                int(nodes[i].removeprefix(config.get("partition.linux.node"))) in range(config.get("partition.linux.booking.range")[0], config.get("partition.linux.booking.range")[1]+1))):

                # p = Process("", args.u, args.n)
                p = Process("", args.u, nodes[i])
                p.start()       # Create a new process and invoke the Process.run() method
                p.join()        # Process.join() to wait for task completion
            else:
                # print (f"< {args.n} > is not in bookable range") if MyPrintCondition.fprint else 0
                print (f"< {args.n} > is not in bookable range") if verbose.mode else 0
                logger.info (f"< {args.n} > is not in bookable range")


if __name__ == '__main__':
    main()