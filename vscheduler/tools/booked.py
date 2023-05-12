# management script for bookable partition
import multiprocessing, click
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.modules.booked.host import host_by_name                            # retreives host identification in booked
from vscheduler.modules.booked.resource import resource_reservations               # retreives series id of each resource
from vscheduler.modules.booked.reservation import user_reservations_by_user_id     # retreives reservation instance id of bookings for each user
from vscheduler.modules.cluster.who import who                                     # who's logged in each node
from vscheduler.modules.booked.user import user_details_by_username                # retreives user identification in booked
from vscheduler.modules.booked.instances import reservation_instances              # retreives reservation instance id, series id, and timeline of bookings for determined time bracket
from vscheduler.modules.booked.deleted import deleted                              # retreives status id of each reservation instances
from vscheduler.modules.cluster.logoff import logoff


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
        user = ""
        # time.sleep(1)
        print ("\n==>> Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        resource_id = host_by_name(self.hostname)                                                   # retreives node resource id
        series_ids = resource_reservations(resource_id) if resource_id else quit()  # NO BOOKING AT ALL               # retreives node series ids
        users = who(self.hostname) if not self.username else [self.username]                        # retreives node logged in users
        print (f"\nusers logged in or asked to be checked in <", self.hostname, ">:", users) if MyPrintCondition.fprint else 0
        instances = reservation_instances(MyBrackets.start_bracket, MyBrackets.end_bracket)         # retreives booking records within time brackets

        if users:
            for user in users:
                self.found = False
                self.del_found = False
                print ("\n--> user:", user) if MyPrintCondition.fprint else 0
                user_identity = user_details_by_username(user)                                      # retreives user identification
                if user_identity:
                    reservations = user_reservations_by_user_id(user_identity[0][0])                # retreives user booking records
                else: 
                    print (f"user <", user, "> does not exist in booked db")
                    continue    
                # print (f"reservations for", user, reservations)
                if instances:
                    for instance in instances:
                        print ("instance", instance)
                        print ("instance[3]",instance[3])
                        if instance[1] <= MyBrackets.now and instance[2] >= MyBrackets.now:         # if the booking is current
                            print ("booking for the current time") if MyPrintCondition.fprint else 0
                            if not any(instance[3] in x for x in series_ids):
                                print (f"none of reservation instances records matches booking(s) made for <", self.hostname, ">")
                                exit
                            else:
                                for series_id in series_ids:
                                    print ("series_id[0]", series_id[0])
                                    if series_id[0] == instance[3]:
                                        if not any(instance[0] in x for x in reservations):
                                            print (f"none of records matches booking made by <", user, ">")
                                        else:
                                            for reservation in reservations:
                                                print ("reservation", reservation)
                                                print ("reservation[0]", reservation[0])
                                                print ("instance[0]", instance[0])
                                                if reservation[0] == instance[0]:
                                                    if deleted(instance[3])[0][1] != 2:     # checks if booking is deleted
                                                        # if reservation[1] == user_identity[0]:
                                                        # **** add a condition here to make sure booking is for now ****
                                                        self.found = True
                                                        print ("all good")
                                                        break
                                                    else:
                                                        self.del_found = True
                                                        print ("deleted record") if MyPrintCondition.fprint else 0
                                                else:
                                                    print (f"booking record not for <", user, ">") if MyPrintCondition.fprint else 0
                                    else:
                                        print (f"record of <", self.hostname, "> does not match this booking") if MyPrintCondition.fprint else 0
                        else:
                            print ("booking not for the current time") if MyPrintCondition.fprint else 0
                else:
                    print ("no current booking for <", self.hostname, "> in the time bracket set in the config - skipping and killing all sessions") if MyPrintCondition.fprint else 0
                    logoff(user, self.hostname)
                    continue
                if self.found == True:
                    print (f"matched the booking for <", user, "> - session on <", self.hostname, "> is valid") if MyPrintCondition.fprint else 0
                else:
                    if not self.del_found:
                        print (f"no match found for <", user, "> on <", self.hostname, "> - session will be killed") if MyPrintCondition.fprint else 0
                    else:
                        print (f"booking for <", user, "> on <", self.hostname, "> has been deleted - session will be killed") if MyPrintCondition.fprint else 0
                    logoff(user, self.hostname)       
        else:
            print (f"no one is using <", self.hostname, "> - skipping") if MyPrintCondition.fprint else 0


def main():
    MyBrackets.what_time(MyBrackets.now, MyBrackets.start_bracket, MyBrackets.end_bracket)
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