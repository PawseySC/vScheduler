# called by vinfo tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
from tabulate import tabulate
import pandas as pd
import numpy as np
import pandas as pd

my_connection = MyDatabase.connect_report_db()

records = Capture_log("status", __file__)
logger = records.log_agent("info")

linux_general_nodes = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
linux_booking_nodes = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
windows_general_nodes = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
windows_booking_nodes = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
        

def print_info():
    try:
        query = f"SELECT node, status, pool from status WHERE start = end"
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(query)
            query_results = my_cursor.fetchall()
        # print ("\n", tabulate(query_results, headers=['node', 'status', 'pool'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
        # logger.info ("\n" + tabulate(query_results, headers=['node', 'status', 'pool'], tablefmt='psql'))
        
        ongoing_status = np.array(query_results)
        print (f"ongoing_status: {ongoing_status}")
        # print (f'query_results[np.where(np.array(query_results) == node)[0][1]]: {np.where(a == "setonix-vis05")[0][0]}')
        # print (f"linux_general_hosts: {linux_general_hosts}")
        sentence = []
        all_nodes = [linux_general_nodes, linux_booking_nodes, windows_general_nodes, windows_booking_nodes]
        print (linux_general_nodes, "\n", linux_booking_nodes, "\n", windows_general_nodes, "\n", windows_booking_nodes)
        for nodes in all_nodes:
            
            
            # print (f"nodes {nodes}")
            
            for node in nodes:
                # print (node, "--->>> YESYESYES" if node in (linux_general_nodes or windows_general_nodes) else "NONONO")
                # print (f"node: {node}")
                if node in np.array(query_results)[:,0]:
                    # print (f"{node} currently in db")
                    sentence.insert(len(sentence), [MyCredentials.linux_pool if MyCredentials.linux_node_name in node else MyCredentials.windows_pool, 
                                                    query_results[np.where(ongoing_status == node)[0][0]][2], 
                                                    "up" if (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)) or
                                                            (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)) or
                                                            (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)) or
                                                            (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1))
                                                            else "down",                                                    query_results[np.where(ongoing_status == node)[0][0]][1], 
                                                    node])
                else:
                    sentence.insert(len(sentence), [MyCredentials.linux_pool if MyCredentials.linux_node_name in node else MyCredentials.windows_pool, 
                                                    "general" if node in (linux_general_nodes or windows_general_nodes) else "booking", 
                                                    "up" if (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)) or
                                                            (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)) or
                                                            (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)) or
                                                            (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1))
                                                            else "down", 
                                                    "idle", 
                                                    node])
            idle = sum(x.count('idle') for x in sentence)
            down = sum(x.count('down') for x in sentence)
            maint = sum(x.count('maint') for x in sentence)
            reserved = sum(x.count('reserved') for x in sentence)
            allocated = sum(x.count('allocated') for x in sentence)
            # print (idle, reserved, allocated, down, maint)
            # print (f"idle: {idle}")
            hosts = pd.DataFrame(list(sentence))
            hosts.columns = ["SYSTEM", "PARTITION", "AVAIL", "STAT", "NODELIST"]
            hosts.insert(3, "NODE", "", True)
            pd.set_option('display.colheader_justify', 'left')
            print (hosts.to_string(index = False))
            
            
            host_copy = hosts[hosts['STAT'] == 'maint']
            print (f"hosts_copy: {host_copy}")
            print (f"host_copy.count: {host_copy['NODELIST'].count()}")
            tedad = f"host_copy.count: {host_copy['NODELIST'].count()}"
            print (MyCredentials.linux_pool if host_copy[host_copy['STAT'] == 'maint']['NODELIST'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool)
            whichsystem = MyCredentials.linux_pool if host_copy[host_copy['STAT'] == 'maint']['NODELIST'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool
            print ()
            final_sentence=[]
            final_sentence.insert (len(final_sentence), [whichsystem, host_copy[host_copy['STAT'] == 'maint']['PARTITION']])
            print (f"final_sentence: {final_sentence}")
            
            status_list = ["idle", "down", "maint", "reserved", "allocated"]
            # final_list2 = pd.DataFrame("SYSTEM", "PARTITION", "AVAIL", "NODE", "STAT", "NODELIST")
            for status in status_list:
                
                
                final_list = []
                # node_numbers = list(hosts[hosts['STAT'] == status]['NODELIST'].replace({MyCredentials.linux_node_name : ""}, regex=True)) if MyCredentials.linux_node_name in hosts[hosts['STAT' == status]]['NODELIST'].any else list(hosts[hosts['STAT'] == status]['NODELIST'].replace({MyCredentials.windows_node_name : ""}, regex=True)) # gets node numbers with specific status
                # node_numbers_int = [int(i) for i in node_numbers]
                # print (f"node_numbers_int: {node_numbers_int}")
                # a= [i.replace("'", "") for i in a]
                node_count = hosts[hosts['STAT'] == status]['STAT'].count()
                print (f"node_count: {node_count}")
                # print ( f"{hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name)}")
                # print ("yes" if{MyCredentials.linux_pool if MyCredentials.linux_node_name in hosts[hosts['STATUS'] == status]['NODE'].values else MyCredentials.windows_pool} else "no")
                # print (f"{hosts[hosts['STATUS'] == status]['POOL']}")
                # print (f"{hosts[hosts['STATUS'] == status]['NODE']}")
                # print (f"{MyCredentials.linux_node_name}" if f"{hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name)}" else f"{MyCredentials.windows_node_name}")
                # print ("1" if hosts[hosts["STATUS"]==status]['NODE'].str.contains("setonix").any else "2")
                # print (hosts[hosts["STATUS"]=='down']['NODE'].values)
                # print ("Y" if "setonix" in hosts[hosts['STATUS'] == status]['NODE'].values else "N")
                # print ("Y" if hosts[hosts['STATUS'] == status]['NODE'].str.contains("L") else "N")
                # a = MyCredentials.linux_pool if hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name) else MyCredentials.windows_pool
                # print (f"a: {a}")
                # final_list3 = {"SYSTEM": [MyCredentials.linux_pool if hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool],
                #                "PARTITION": [hosts[hosts['STATUS'] == status]['POOL']],
                #                "AVAIL": [""],
                #                "NODES": node_count,
                #                "STAT": [hosts[hosts['STATUS'] == status]['NODE']],
                #                "NODELIST": [MyCredentials.linux_node_name + str(node_numbers_int)]}
                # df = pd.DataFrame(final_list3)
                # print (df.to_string(index=False))
                # final_list.insert(len(final_list), [MyCredentials.linux_pool if hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool, hosts[hosts['STATUS'] == status]['POOL'], "", hosts[hosts['STATUS'] == status]['NODE'], status, MyCredentials.linux_node_name + str(node_numbers_int)])
                # print (final_list)
            # "up" if MyCredentials.linux_general else "down"
            # d = pd.DataFrame(list(final_list))
            # d.columns = ["SYSTEM", "PARTITION", "AVAIL", "NODE", "STAT", "NODELIST"]
            # pd.set_option('display.colheader_justify', 'left')
            # d = d.style.set_properties(**{'text-align': 'left'})
            # print (d.to_string(index = False))
        # for node in linux_booking_hosts:
        #     if node in np.array(query_results)[:,0]:
        #         print (f"{node} currently in db")
        #         sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
        #     else:
        #         sentence.insert(len(sentence), [node, "idle", "booking"])
        # for node in windows_general_hosts:
        #     if node in np.array(query_results)[:,0]:
        #         print (f"{node} currently in db")
        #         sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
        #     else:
        #         sentence.insert(len(sentence), [node, "idle", "general"])
        # for node in windows_booking_hosts:
        #     if node in np.array(query_results)[:,0]:
        #         print (f"{node} currently in db")
        #         sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
        #     else:
        #         sentence.insert(len(sentence), [node, "idle", "booking"])
        # print (f"sentence: {sentence}")
        # print ("\n", tabulate(sentence, headers=['node', 'status', 'pool'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
        # logger.info ("\n" + tabulate(sentence, headers=['node', 'status', 'pool'], tablefmt='psql'))
                    
    except my_connection.Error as e:
        print (f"status query hit error\n{e}") if MyPrintCondition.fprint else 0
        logger.error (f"status query hit error\n{e}")
        
        
def session (node):
    cluster = MyCredentials.report_linux_table if MyCredentials.linux_node_name in node else MyCredentials.report_windows_table
    query = f"SELECT node, user, pool, start, end from {cluster} WHERE node = '{node}' AND start = end"
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(query)
        query_results = my_cursor.fetchall()
    # print (query, query_results)
    # a = dict(query_results)
    if query_results and (node in linux_general_nodes or node in windows_general_nodes):
        print (f"\nLogged-in Users in < {node} >, {cluster} cluster\n", tabulate(query_results, headers=['node', 'user', 'pool', 'start', 'end'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
        logger.info (f"\nLogged-in Users in < {node} >, {cluster} cluster\n" + tabulate(query_results, headers=['node', 'user', 'pool', 'start', 'end'], tablefmt='psql'))
    else:
        print (f"No one's logged in to < {node} >")
        logger.info (f"No one's logged in to < {node} >")