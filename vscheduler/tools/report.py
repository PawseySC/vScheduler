import multiprocessing
from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.timer import Brackets as MyBrackets
# from vscheduler.general.alert import mailFunction
# from vscheduler.modules.booked.reservation import user_reservations
# from vscheduler.modules.booked.deleted import deleted_records
# from vscheduler.modules.booked.host import host_by_name                            # retreives host identification in booked
# from vscheduler.modules.booked.resource import resource_reservations               # retreives series id of each resource
# from vscheduler.modules.booked.reservation import user_reservations_by_user_id     # retreives reservation instance id of bookings for each user
# from vscheduler.modules.booked.user import user_details_by_username                # retreives user identification in booked
# from vscheduler.modules.booked.instances import reservation_instances              # retreives reservation instance id, series id, and timeline of bookings for determined time bracket
# from vscheduler.modules.booked.deleted import deleted                              # retreives status id of each reservation instances
# from vscheduler.modules.cluster.who import who                                     # who's logged in each node
# from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.reports.report_pool import pool_report_generator
from tabulate import tabulate
# my_connection = MyDatabase.connect_booked_db()
# my_cursor = my_connection.cursor()

report_records = CaptureLog("report", __file__)
logger = report_records.log_agent("tools")

# sendMail = True
# counter = 0
# status = ""
# dataReport_time =[]
# fontColor = "white"
# resolutionColor = "grey"
# cumulativeDailyBooked = 0
# cumulativeDailyActual = 0
# cumulativeDailyAdmin = 0
# cumulativeWeeklyBooked = 0
# cumulativeWeeklyActual = 0
# cumulativeWeeklyAdmin = 0
# cumulativeMonthlyBooked = 0
# cumulativeMonthlyActual = 0
# cumulativeMonthlyAdmin = 0
# cumulativeQuarterlyBooked = 0
# cumulativeQuarterlyActual = 0
# cumulativeQuarterlyAdmin  = 0
# cumulativeAnnuallyBooked = 0
# cumulativeAnnuallyActual = 0
# cumulativeAnnuallyAdmin = 0
# noActualDailyUsage = ""
# noActualWeeklyUsage = ""
# noActualMonthlyUsage = ""
# noActualQuarterlyUsage = ""
# noActualAnnualUsage = ""



# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username

    def run(self):
        """
        Report script
        """
        # time.sleep(1)
        print ("\n==>> Process id: {}".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        # if Config.config['partition']['windows']['node'] in self.hostname:
        #     logger_win.info ("==>Process id: {}".format(self.id)) if self.id else 0
        # elif Config.config['partition']['linux']['node'] in self.hostname:
        #     logger_unix.info ("==>Process id: {}".format(self.id)) if self.id else 0
        logger.info ("==>Process id: {}".format(self.id)) if self.id else 0

        start = '2000-01-01' if not initiate.start else initiate.start
        end = MyBrackets.local_time if not initiate.end else initiate.end
        print (f"start: {start}")
        print (f"end: {end}")
        pool_report_generator(self.hostname, self.username, start, end)
        
        # if (Config.config['partition']['windows']['node'] in self.hostname and int(self.hostname.replace(Config.config['partition']['windows']['node'], "")) in MyCredentials.windows_booking_range) \
        #     or (Config.config['partition']['linux']['node'] in self.hostname and int(self.hostname.replace(Config.config['partition']['linux']['node'], "")) in MyCredentials.linux_booking_range):
        #     print (f"\nbooking report for node: {self.hostname}") if MyPrintCondition.fprint and self.id else 0
        #     logger.info (f"\nbooking report for node: {self.hostname}") if MyPrintCondition.fprint and self.id else 0

        #     if self.username:
        #         print (f"\nonly for given username: {self.username}") if MyPrintCondition.fprint and self.id else 0
        #         logger.info (f"\nonly for given username: {self.username}") if MyPrintCondition.fprint and self.id else 0
        #     else:
        #         print ("\nreport for all usernames because username is not given") if MyPrintCondition.fprint and self.id else 0
        #         logger.info ("\nreport for all usernames because username is not given") if MyPrintCondition.fprint and self.id else 0

        # elif (Config.config['partition']['windows']['node'] in self.hostname and int(self.hostname.replace(Config.config['partition']['windows']['node'], "")) in MyCredentials.windows_general_range) \
        #     or (Config.config['partition']['linux']['node'] in self.hostname and int(self.hostname.replace(Config.config['partition']['linux']['node'], "")) in MyCredentials.linux_general_range):
        #     print (f"\npool report for node: {self.hostname}") if MyPrintCondition.fprint and self.id else 0
        #     logger.info (f"\npool report for node: {self.hostname}") if MyPrintCondition.fprint and self.id else 0
       
        #     if self.username:
        #         print (f"\nonly for given username: {self.username}") if MyPrintCondition.fprint and self.id else 0
        #         logger.info (f"\nonly for given username: {self.username}") if MyPrintCondition.fprint and self.id else 0
        #         # pool_report_generator(self.hostname, self.username, '2023-05-01 00:00:00', '2023-09-01 00:00:00')
        #         start = '2000-01-01' if not initiate.start else initiate.start
        #         end = MyBrackets.local_time if not initiate.end else initiate.end
        #         print (f"start: {start}")
        #         print (f"end: {end}")
        #         pool_report_generator(self.hostname, self.username, start, end)
        #     else:
        #         print ("\nreport for all usernames because username is not given") if MyPrintCondition.fprint and self.id else 0
        #         logger.info ("\nreport for all usernames because username is not given") if MyPrintCondition.fprint and self.id else 0
        #         response = pool_report_generator(self.hostname, self.username, '', '')
        


        # resource_id = host_by_name(self.hostname) if self.hostname else ""                                            # retreives node resource id
        # series_ids = resource_reservations(resource_id) if resource_id else quit()  # NO BOOKING AT ALL               # retreives node series ids
        # reservations = user_reservations()
        # deletion_status = deleted_records()
        # users = who(self.hostname) if not self.username else [self.username]                        # retreives node logged in users
        # print (f"\nusers logged in or asked to be checked in <", self.hostname, ">:", users) if MyPrintCondition.fprint else 0
        # instances = reservation_instances(MyBrackets.start_bracket, MyBrackets.end_bracket)         # retreives booking records within time brackets


def main():
    # if not initiate.node:
    #     for i in range (MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
    #         node = Config.config['partition']['windows']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['windows']['node'] + str(i)
    #         p = Process(i, initiate.user, node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     for i in range (MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
    #         node = Config.config['partition']['windows']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['windows']['node'] + str(i)
    #         p = Process(i, initiate.user, node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     for i in range (MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
    #         node = Config.config['partition']['linux']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['linux']['node'] + str(i)
    #         p = Process(i, initiate.user, node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     for i in range (MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
    #         node = Config.config['partition']['linux']['node'] + '0' + str(i) if i <= 9 else Config.config['partition']['linux']['node'] + str(i)
    #         p = Process(i, initiate.user, node)
    #         p.start()       # Create a new process and invoke the Process.run() method
    #         p.join()        # Process.join() to wait for task completion
    #     # for i in range (MyCredentials.range[0], MyCredentials.range[1]):
    #     #     node = MyCredentials.node_name + '0' + str(i) if i <= 9 else MyCredentials.node_name + str(i)
    #     #     p = Process(i, initiate.user, node)
    #     #     p.start()       # Create a new process and invoke the Process.run() method
    #     #     p.join()        # Process.join() to wait for task completion
    # else:
    #     p = Process("", initiate.user, initiate.node)
    #     p.start()       # Create a new process and invoke the Process.run() method
    #     p.join()        # Process.join() to wait for task completion
    p = Process("", initiate.user, initiate.node)
    p.start()       # Create a new process and invoke the Process.run() method
    p.join()        # Process.join() to wait for task completion

if __name__ == '__main__':
    main()