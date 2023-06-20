# quota script
import multiprocessing, click
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.booked.group import group_id
from vscheduler.modules.booked.group import group_name
from vscheduler.modules.booked.group import group_members
from vscheduler.modules.booked.user import user_details_by_username
from vscheduler.modules.booked.host import host_by_name
from vscheduler.modules.booked.host import host_by_id
from vscheduler.modules.booked.quotas import quotas
from vscheduler.modules.booked.user import user_details_by_user_id
from rich.console import Console
from rich.table import Table


# Process class
class Process(multiprocessing.Process):
    def __init__(self, id, username, node):
        super(Process, self).__init__()
        self.id = id
        self.hostname = node
        self.username = username
        self.found = False
    
    def run(self):
        quotas_query = []
        resource_id = groups_id = ""
        # time.sleep(1)
        print("\n==>Process id: {}\n".format(self.id)) if MyPrintCondition.fprint and self.id else 0
        user_id = user_details_by_username(self.username)[0][0] if self.username else ""
        groups_ids = group_id(user_id) if user_id else ""
        resource_id = host_by_name(self.hostname)[0][0] if self.hostname and host_by_name(self.hostname) else ""
        if not resource_id:
            print (f"no resource record for <", self.hostname, "> in booked - skipping") if MyPrintCondition.fprint else print (f"no quota found on <", self.hostname, ">")
            quit()
        if groups_ids:
            for groups_id in groups_ids: 
                quotas_query.append(quotas(resource_id, groups_id[1]))
                # quotas_query = quotas(resource_id, groups_id[1])
        else: 
            # quotas_query = quotas(resource_id, "")
            quotas_query.append(quotas(resource_id, ""))
        if len(quotas_query[0]):
            if self.id == MyCredentials.range[0] or not self.id:
                console = Console()
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("username", style="dim", width=15) if self.username else 0
                table.add_column("group/project", style="dim", width=15)
                table.add_column("quota", width=12)
                table.add_column("each", justify="right", width=8)
                # table.add_column("enforced day(s)|start|end", justify="right")
                table.add_column("on", justify="right", width=8)
                table.add_column("inequally shared between", justify="right")
            else:
                console = Console()
                table = Table(show_header=False)
                table.add_column(style="dim", width=15) if self.username else 0
                table.add_column(style="dim", width=15)
                table.add_column(width=12)
                table.add_column(justify="right", width=8)
                # table.add_column(justify="right")
                table.add_column(justify="right", width=8)
                table.add_column(justify="right")
            for quotas_query_row in quotas_query:
                for quota in quotas_query_row:
                    quota_limit = quota[1]
                    unit = quota[2]
                    duration = quota[3]
                    resource_id = quota[4]
                    group__id = quota[5]
                    # schedule_id = quota[6]
                    enforced_days = quota[7]
                    enforced_time_start = quota[8]
                    enforced_time_end = quota[9]
                    member_username = []
                    members_id = group_members(group__id)
                    for member_id in members_id:
                        member_username.append(user_details_by_user_id(member_id)[0][3])
                    if not user_id:
                        table.add_row(group_name(group__id)[0][1] ,str(quota_limit) + " " + str(unit), duration, self.hostname, str(member_username)) if self.hostname else table.add_row(group_name(group__id)[0][1] ,str(quota_limit) + " " + str(unit), duration, host_by_id(resource_id), str(member_username))
                        if MyPrintCondition.fprint:
                            if self.hostname:
                                print ("\ngroup/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced", enforced_days, "starting", enforced_time_start, "till", enforced_time_end, "on <", self.hostname, "> inequally shared between", member_username, "\n") if enforced_days and enforced_time_start else print ("\ngroup/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced EveryDay AllDays on <", self.hostname, "> inequally shared between", member_username, "\n")
                            else:
                                print ("\ngroup/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced", enforced_days, "starting", enforced_time_start, "till", enforced_time_end, "on <", host_by_id(resource_id), "> inequally shared between", member_username, "\n") if enforced_days and enforced_time_start else print ("\ngroup/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced EveryDay AllDays on <", host_by_id(resource_id), "> inequally shared between", member_username, "\n")
                    else:
                        table.add_row(self.username, group_name(group__id)[0][1] ,str(quota_limit) + " " + str(unit), duration, self.hostname, str(member_username)) if self.hostname else table.add_row(self.username, group_name(group__id)[0][1] ,str(quota_limit) + " " + str(unit), duration, host_by_id(resource_id), str(member_username))
                        if MyPrintCondition.fprint:
                            if self.hostname:
                                print ("\nuser <", self.username, "> as a member of group/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced", enforced_days, "starting", enforced_time_start, "till", enforced_time_end, "on <", self.hostname, "> inequally shared between", member_username, ">\n") if enforced_days and enforced_time_start else print ("\nuser <", self.username, "> as a member of group/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced EveryDay AllDays on <", self.hostname, "> inequally shared between", member_username, ">\n")
                            else:
                                print ("\nuser <", self.username, "> as a member of group/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced", enforced_days, "starting", enforced_time_start, "till", enforced_time_end, "on <", host_by_id(resource_id), "> inequally shared between", member_username, ">\n") if enforced_days and enforced_time_start else print ("\nuser <", self.username, "> as a member of group/project <", group_name(group__id)[0][1], "> has quota of <", quota_limit, unit, "> each <", duration, "> enforced EveryDay AllDays on <", host_by_id(resource_id), "> inequally shared between", member_username, ">\n")
            console.print(table)
        else:
            print ("no quota found for <", self.username, "> on <", self.hostname, ">") if self.username else print ("no quota found on <", self.hostname, ">")


def main():
    if not initiate.node and not initiate.user:
        if MyCredentials.windows_booking or MyCredentials.linux_booking:
            if MyCredentials.windows_booking:
                for i in range (MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]):
                    node = MyCredentials.windows_node_name + '0' + str(i) if i <= 9 else MyCredentials.windows_node_name + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
            if MyCredentials.linux_booking:
                for i in range (MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]):
                    node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
                    p = Process(i, initiate.user, node)
                    p.start()       # Create a new process and invoke the Process.run() method
                    p.join()        # Process.join() to wait for task completion
        else:
            print ("There is no bookable Windows or Linux partition; To enable it edit vscheduler confilg") if MyPrintCondition.fprint else 0
    else:
        if (MyCredentials.windows_node_name in initiate.node and 
                int(initiate.node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]) or 
                (MyCredentials.linux_node_name in initiate.node and 
                int(initiate.node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]))):
            p = Process("", initiate.user, initiate.node)
            p.start()       # Create a new process and invoke the Process.run() method
            p.join()        # Process.join() to wait for task completion
        else:
            print ("<", initiate.node, "> is not in bookable range") if MyPrintCondition.fprint else 0
            

if __name__ == '__main__':
    main()