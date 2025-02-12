import multiprocessing, click
from vscheduler.log.log import CaptureLog
from vscheduler.lib import config
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.modules.booked.host import host_by_name                                # retreives host identification in booked
from vscheduler.modules.booked.resource import resource_reservations                   # retreives series id of each resource
from vscheduler.modules.booked.reservation import user_reservations_by_instance_id     # retreives reservation instance id of bookings for each user
from vscheduler.modules.booked.user import user_details_by_user_id                     # retreives user identification in booked
from vscheduler.modules.booked.instances import reservation_instances                  # retreives reservation instance id, series id, and timeline of bookings for determined time bracket
from vscheduler.modules.booked.deleted import deleted                                  # retreives status id of each reservation instances
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guaca_user_group import guacamole_user_group
from vscheduler.modules.guaca.check_group import check_group
from vscheduler.modules.guaca.insert import insert
from vscheduler.modules.guaca.update import update
from vscheduler.modules.guaca.modify import modify

guaca_records = CaptureLog("guaca", __file__)
logger = guaca_records.log_agent("tools")


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
        Sync script for bookable partition
        """
        # time.sleep(1)
        print("\n==>Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        logger.info ("==>Process id: {}".format(self.id)) if self.id else 0
        instances = reservation_instances(MyBrackets.start_bracket, MyBrackets.end_bracket)     # retreives booking records within time brackets
        resource_id = host_by_name(self.hostname)                                               # retreives node resource id
        series_ids = resource_reservations(resource_id[0][0]) if resource_id else exit                # retreives node series ids

        if resource_id:
            if series_ids:
                if instances:
                    for instance in instances:
                        print (f"instance: {instance}") if MyPrintCondition.fprint else 0
                        logger.info (f"instance: {instance}")
                        if not any(instance[3] in x for x in series_ids):
                            print (f"booking does not belong to < {self.hostname} > - skipping") if MyPrintCondition.fprint else 0
                            logger.info (f"booking does not belong to < {self.hostname} > - skipping")
                        else:                                          
                            print ("\nfound a match") if MyPrintCondition.fprint else 0
                            logger.info ("\nfound a match")
                            if instance[1] <= MyBrackets.now and instance[2] >= MyBrackets.now:         # if the booking is current
                                print ("booking for the current time") if MyPrintCondition.fprint else 0
                                logger.info ("booking for the current time")
                                reservations = user_reservations_by_instance_id(instance[0])            # retreives user booking records
                                node_user = user_details_by_user_id(reservations[0][1])                 # retreives user identification
                                user_entity = entity(node_user[0][3])
                                group_entity = entity(self.hostname)
                                user_group = guacamole_user_group(group_entity[0][0])
                                group_check = check_group (user_group[0][0])
                                if deleted(instance[3])[0][1] == 2:                                     # checks if booking is deleted
                                    print ("deleted booking") if MyPrintCondition.fprint else 0
                                    logger.info ("deleted booking")
                                    modify(user_entity[0][0], user_group[0][0])
                                else:
                                    self.found = True
                                    if not group_check or not any(user_entity[0][0] in x for x in group_check):
                                        insert(user_entity[0][0], user_group[0][0])
                                    elif group_check and any(user_entity[0][0] in x for x in group_check):
                                        for row_group_check in group_check:
                                            if row_group_check[1] == user_entity[0][0]:
                                                pool_entity = entity(config.partition['windows']['node']) if config.partition['windows']['node'] in self.hostname else entity(config.partition['linux']['node'])
                                                pool_user_group = guacamole_user_group(pool_entity[0][0])
                                                update(user_entity[0][0], user_group[0][0], pool_user_group[0][0], "sync", config.partition['windows']['node'] if config.partition['windows']['node'] in self.hostname else config.partition['linux']['node'])
                                                break
                            else:
                                print ("booking not for the current time") if MyPrintCondition.fprint else 0
                                logger.info ("booking not for the current time")
                else:
                    print (f"no current booking for < {self.hostname} > in the time bracket set in the config - skipping") if MyPrintCondition.fprint else 0
                    logger.info (f"no current booking for < {self.hostname} > in the time bracket set in the config - skipping")
                    quit()
            else:
                print (f"no booking for < {self.hostname} > - skipping") if MyPrintCondition.fprint else 0
                logger.info (f"no booking for < {self.hostname} > - skipping")
                quit()
        else:
            print (f"no resource in booked with name < {self.hostname} > - skipping") if MyPrintCondition.fprint else 0
            logger.info (f"no resource in booked with name < {self.hostname} > - skipping")
            quit()
        
        if self.found == False:
            modify("", guacamole_user_group(entity(self.hostname)[0][0])[0][0])                     # remove all links in guacamole for this node


def main():
    MyBrackets.what_time(MyBrackets.now, MyBrackets.local_time, MyBrackets.start_bracket, MyBrackets.end_bracket)
    if not initiate.node:
        if config.partition['windows']['booking']['status'] or config.partition['linux']['booking']['status']:
            if config.partition['windows']['booking']['status']:
                for i in range (config.partition['windows']['booking']['range'][0], config.partition['windows']['booking']['range'][1]+1):
                    node = config.partition['windows']['node'] + '0' + str(i) if i <= 9 else config.partition['windows']['node'] + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if config.partition['linux']['booking']['status']:
                for i in range (config.partition['linux']['booking']['range'][0], config.partition['linux']['booking']['range'][1]+1):
                    node = config.partition['linux']['node'] + '0' + str(i) if i <= 9 else config.partition['linux']['node'] + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no bookable Windows or Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
            logger.info ("There is no bookable Windows or Linux partition; To enable it edit vscheduler confilg")
    else:
        if (config.partition['windows']['node'] in initiate.node and 
                int(initiate.node.removeprefix(config.partition['windows']['node'])) in range(config.partition['windows']['booking']['range'][0], config.partition['windows']['booking']['range'][1]+1) or 
                (config.partition['linux']['node'] in initiate.node and 
                int(initiate.node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['booking']['range'][0], config.partition['linux']['booking']['range'][1]+1))):
            p = Process("", initiate.user, initiate.node)
            p.start()       # Create a new process and invoke the Process.run() method
            p.join()        # Process.join() to wait for task completion
        else:
            print (f"< {initiate.node} > is not in bookable range") if MyPrintCondition.fprint else 0
            logger.info (f"< {initiate.node} > is not in bookable range")


if __name__ == '__main__':
    main()
