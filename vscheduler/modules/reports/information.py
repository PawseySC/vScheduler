# called by vinfo tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
from tabulate import tabulate
from functools import reduce
import pandas as pd
import numpy as np
import pandas as pd
import re

my_connection = MyDatabase.connect_report_db()

records = Capture_log("status", __file__)
logger = records.log_agent("info")

pd.set_option('display.colheader_justify', 'left')
pd.options.display.max_colwidth = 100
        
linux_general_nodes = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
linux_general_nodes = pd.DataFrame(list(linux_general_nodes))
linux_general_nodes.columns = ['NODE']
linux_general_nodes.insert(0, 'SYSTEM', MyCredentials.linux_pool)
linux_general_nodes.insert(1, 'PARTITION', "general")
linux_general_nodes.insert(2, 'AVAIL', "up" if MyCredentials.linux_general else "down")
linux_general_nodes.insert(3, 'NODES', 1)

linux_reservation_nodes = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
linux_reservation_nodes = pd.DataFrame(list(linux_reservation_nodes))
linux_reservation_nodes.columns = ['NODE']
linux_reservation_nodes.insert(0, 'SYSTEM', MyCredentials.linux_pool)
linux_reservation_nodes.insert(1, 'PARTITION', "reservation")
linux_reservation_nodes.insert(2, 'AVAIL', "up" if MyCredentials.linux_booking else "down")
linux_reservation_nodes.insert(3, 'NODES', 1)

windows_general_nodes = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
windows_general_nodes = pd.DataFrame(list(windows_general_nodes))
windows_general_nodes.columns = ['NODE']
windows_general_nodes.insert(0, 'SYSTEM', MyCredentials.windows_pool)
windows_general_nodes.insert(1, 'PARTITION', "general")
windows_general_nodes.insert(2, 'AVAIL', "up" if MyCredentials.windows_general else "down")
windows_general_nodes.insert(3, 'NODES', 1)

windows_reservation_nodes = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1)]
windows_reservation_nodes = pd.DataFrame(list(windows_reservation_nodes))
windows_reservation_nodes.columns = ['NODE']
windows_reservation_nodes.insert(0, 'SYSTEM', MyCredentials.windows_pool)
windows_reservation_nodes.insert(1, 'PARTITION', "reservation")
windows_reservation_nodes.insert(2, 'AVAIL', "up" if MyCredentials.windows_booking else "down")
windows_reservation_nodes.insert(3, 'NODES', 1)

all_nodes = [linux_general_nodes, linux_reservation_nodes, windows_general_nodes, windows_reservation_nodes]
# all_nodes_merged = reduce(lambda left, right: pd.merge(left, right, on='NODE'), dfs)
all_nodes_merged = pd.concat(all_nodes, axis=0)

# all_nodes_merged = reduce(lambda df_left,df_right: pd.merge(df_left, df_right, 
                                            # left_index=True, right_index=True, 
                                            # how='outer'), 
                                            # [linux_general_nodes, linux_reservation_nodes, windows_general_nodes, windows_reservation_nodes]).fillna('nan_value')
# reduce(lambda  left,right: pd.merge(left,right,on=['NODE'], how='outer'), [linux_general_nodes, linux_reservation_nodes, windows_general_nodes, windows_reservation_nodes])
# all_nodes_merged = pd.concat([linux_general_nodes, linux_reservation_nodes, windows_general_nodes, windows_reservation_nodes], join='outer', axis=1).fillna('')
# all_nodes = pd.merge(linux_general_nodes, linux_reservation_nodes, windows_general_nodes, windows_reservation_nodes, on='NODE')


def print_info():
    # print (f"all nodes merged:\n {all_nodes_merged}")
    try:
        query = f"SELECT node, status, pool from status WHERE start = end"
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(query)
            query_results = my_cursor.fetchall()
    except my_connection.Error as e:
            print (f"status query hit error\n{e}") if MyPrintCondition.fprint else 0
            logger.error (f"status query hit error\n{e}")

    if len(query_results) > 0:
        query_results_df = pd.DataFrame(list(np.array(query_results)))
        query_results_df.columns = ['NODE', 'STATUS', 'POOL']
        # print (query_results_df)
                        
        all_nodes_df = all_nodes_merged.merge(query_results_df, on='NODE', how='outer').fillna('idle')
        all_nodes_df = all_nodes_df.drop(['POOL'], axis=1)
        all_nodes_df = all_nodes_df.rename(columns={'STATUS':'STAT'})
        all_nodes_df = all_nodes_df.rename(columns={'NODE':'NODELIST'})
        # shift column 'Name' to first position 
        first_column = all_nodes_df.pop('STAT') 
        # insert column using insert(position, column_name, first_column) function 
        all_nodes_df.insert(4, 'STAT', first_column) 
        # all_nodes_df = all_nodes_df.insert(0, all_nodes_df.STAT, all_nodes_df.pop('STAT'))
        # print (f"all_nodes_df:\n {all_nodes_df.to_string(index=False)}")

        all_nodes_df_categorised = all_nodes_df.groupby(["SYSTEM", "PARTITION", "AVAIL", "STAT"]).sum()
        all_nodes_df_categorised['NODELIST'] = all_nodes_df_categorised['NODELIST'].str.replace('\D+', ' ', regex=True)   # .str.extract('(\d+)', expand=False for extracting numbers only. '\D+' means non-numeric characters.
        # print (f"all_nodes_df_categorised:\n {all_nodes_df_categorised}")
        print (all_nodes_df_categorised)
    else:
        print ("No data in database")

    
# def print_info():
#     try:
#         query = f"SELECT node, status, pool from status WHERE start = end"
#         with my_connection.cursor() as my_cursor:
#             my_cursor.execute(query)
#             query_results = my_cursor.fetchall()
#         # print ("\n", tabulate(query_results, headers=['node', 'status', 'pool'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
#         # logger.info ("\n" + tabulate(query_results, headers=['node', 'status', 'pool'], tablefmt='psql'))
        
#         ongoing_status = np.array(query_results)
#         print (f"ongoing_status: {ongoing_status}")
#         # print (f'query_results[np.where(np.array(query_results) == node)[0][1]]: {np.where(a == "setonix-vis05")[0][0]}')
#         # print (f"linux_general_hosts: {linux_general_hosts}")
#         sentence = []
#         all_nodes = [linux_general_nodes, linux_booking_nodes, windows_general_nodes, windows_booking_nodes]
#         print (linux_general_nodes, "\n", linux_booking_nodes, "\n", windows_general_nodes, "\n", windows_booking_nodes)
#         for nodes in all_nodes:
            
            
#             # print (f"nodes {nodes}")
            
#             for node in nodes:
#                 # print (node, "--->>> YESYESYES" if node in (linux_general_nodes or windows_general_nodes) else "NONONO")
#                 # print (f"node: {node}")
#                 if node in np.array(query_results)[:,0]:
#                     # print (f"{node} currently in db")
#                     sentence.insert(len(sentence), [MyCredentials.linux_pool if MyCredentials.linux_node_name in node else MyCredentials.windows_pool, 
#                                                     query_results[np.where(ongoing_status == node)[0][0]][2], 
#                                                     "up" if (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)) or
#                                                             (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)) or
#                                                             (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)) or
#                                                             (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1))
#                                                             else "down",                                                    query_results[np.where(ongoing_status == node)[0][0]][1], 
#                                                     node])
#                 else:
#                     sentence.insert(len(sentence), [MyCredentials.linux_pool if MyCredentials.linux_node_name in node else MyCredentials.windows_pool, 
#                                                     "general" if node in (linux_general_nodes or windows_general_nodes) else "reservation", 
#                                                     "up" if (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)) or
#                                                             (MyCredentials.linux_node_name in node and int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)) or
#                                                             (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)) or
#                                                             (MyCredentials.windows_node_name in node and int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1))
#                                                             else "down", 
#                                                     "idle", 
#                                                     node])
#             idle = sum(x.count('idle') for x in sentence)
#             down = sum(x.count('down') for x in sentence)
#             maint = sum(x.count('maint') for x in sentence)
#             reserved = sum(x.count('reserved') for x in sentence)
#             allocated = sum(x.count('allocated') for x in sentence)
#         # print (idle, reserved, allocated, down, maint)
#         # print (f"idle: {idle}")
#         hosts = pd.DataFrame(list(sentence))
#         hosts.columns = ["SYSTEM", "PARTITION", "AVAIL", "STAT", "NODELIST"]
#         hosts.insert(3, "NODES", 1, True)
#         # hosts['Result2'] = hosts['SYSTEM'].str.contains('setonix').any()
#         hosts['Result'] = hosts['SYSTEM'].isin(['setonix'])
#         pd.set_option('display.colheader_justify', 'left')
#         pd.options.display.max_colwidth = 100
#         print (hosts.to_string(index = False))
        
#         # cat_hosts = hosts.astype({"AVAIL": "category", "STAT": "category"})
#         # df['Name'] = df['Name'].str.replace('\d+', '')
#         # hosts['NODELIST'] = hosts['NODELIST'].str.replace('\D+', ' ', regex=True)   # .str.extract('(\d+)', expand=False for extracting numbers only. '\D+' means non-numeric characters.
#         print ("+++\n", hosts)
#         print (hosts.to_string(justify='left', index=False))
#         # cond1 = hosts["SYSTEM"].str.contains('setonix')
#         # hosts = hosts["SYSTEM"].mask(cond1, 'M'+hosts["SYSTEM"])
#         # print(hosts)
#         hosts2 = hosts.groupby(["SYSTEM", "PARTITION", "AVAIL", "STAT"]).sum()
#         print("LLLL", hosts2[hosts2['NODELIST'].str.contains("setonix-vis")])
#         hosts2["NODELIST"] = "setonix-vis[" if hosts2['Result'].any() == 0 else "w[" + hosts2["NODELIST"].astype(str) + " ]"
#         # hosts2['NODELIST'] = hosts2['NODELIST'].str.replace('setonix-vis', ' ')
#         print("***\n", hosts2)
#         print (hosts2.isin(['setonix']))
#         hosts2['Result'] = hosts2.eq('setonix').sum(1).gt(1)
        
        
#         print (hosts2)
#         print (hosts)
#         # print (hosts2[hosts2['NODELIST'].str.contains('setonix')].str.replace('setonix-', "Y"))
#         # print ("yessss" if hosts2.loc['setonix'].any() else "nooo")
#         # print(hosts2["NODES"].value_counts()["setonix"])
#         # print("yesyes" if hosts2["NODELIST"].astype(str).str.contains("--").any else "nono")
            
            
#             # host_copy = hosts[hosts['STAT'] == 'maint']
#             # print (f"hosts_copy: {host_copy}")
#             # print (f"host_copy.count: {host_copy['NODELIST'].count()}")
#             # tedad = f"host_copy.count: {host_copy['NODELIST'].count()}"
#             # print (MyCredentials.linux_pool if host_copy[host_copy['STAT'] == 'maint']['NODELIST'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool)
#             # whichsystem = MyCredentials.linux_pool if host_copy[host_copy['STAT'] == 'maint']['NODELIST'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool
#             # print ()
#             # final_sentence=[]
#             # final_sentence.insert (len(final_sentence), [whichsystem, host_copy[host_copy['STAT'] == 'maint']['PARTITION']])
#             # print (f"final_sentence: {final_sentence}")
            
#             # status_list = ["idle", "down", "maint", "reserved", "allocated"]
#             # final_list2 = pd.DataFrame("SYSTEM", "PARTITION", "AVAIL", "NODE", "STAT", "NODELIST")
#             # for status in status_list:
                
                
#                 # final_list = []
#                 # node_numbers = list(hosts[hosts['STAT'] == status]['NODELIST'].replace({MyCredentials.linux_node_name : ""}, regex=True)) if MyCredentials.linux_node_name in hosts[hosts['STAT' == status]]['NODELIST'].any else list(hosts[hosts['STAT'] == status]['NODELIST'].replace({MyCredentials.windows_node_name : ""}, regex=True)) # gets node numbers with specific status
#                 # node_numbers_int = [int(i) for i in node_numbers]
#                 # print (f"node_numbers_int: {node_numbers_int}")
#                 # a= [i.replace("'", "") for i in a]
#                 # node_count = hosts[hosts['STAT'] == status]['STAT'].count()
#                 # print (f"node_count: {node_count}")
#                 # print ( f"{hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name)}")
#                 # print ("yes" if{MyCredentials.linux_pool if MyCredentials.linux_node_name in hosts[hosts['STATUS'] == status]['NODE'].values else MyCredentials.windows_pool} else "no")
#                 # print (f"{hosts[hosts['STATUS'] == status]['POOL']}")
#                 # print (f"{hosts[hosts['STATUS'] == status]['NODE']}")
#                 # print (f"{MyCredentials.linux_node_name}" if f"{hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name)}" else f"{MyCredentials.windows_node_name}")
#                 # print ("1" if hosts[hosts["STATUS"]==status]['NODE'].str.contains("setonix").any else "2")
#                 # print (hosts[hosts["STATUS"]=='down']['NODE'].values)
#                 # print ("Y" if "setonix" in hosts[hosts['STATUS'] == status]['NODE'].values else "N")
#                 # print ("Y" if hosts[hosts['STATUS'] == status]['NODE'].str.contains("L") else "N")
#                 # a = MyCredentials.linux_pool if hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name) else MyCredentials.windows_pool
#                 # print (f"a: {a}")
#                 # final_list3 = {"SYSTEM": [MyCredentials.linux_pool if hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool],
#                 #                "PARTITION": [hosts[hosts['STATUS'] == status]['POOL']],
#                 #                "AVAIL": [""],
#                 #                "NODES": node_count,
#                 #                "STAT": [hosts[hosts['STATUS'] == status]['NODE']],
#                 #                "NODELIST": [MyCredentials.linux_node_name + str(node_numbers_int)]}
#                 # df = pd.DataFrame(final_list3)
#                 # print (df.to_string(index=False))
#                 # final_list.insert(len(final_list), [MyCredentials.linux_pool if hosts[hosts['STATUS'] == status]['NODE'].str.contains(MyCredentials.linux_node_name).any else MyCredentials.windows_pool, hosts[hosts['STATUS'] == status]['POOL'], "", hosts[hosts['STATUS'] == status]['NODE'], status, MyCredentials.linux_node_name + str(node_numbers_int)])
#                 # print (final_list)
#             # "up" if MyCredentials.linux_general else "down"
#             # d = pd.DataFrame(list(final_list))
#             # d.columns = ["SYSTEM", "PARTITION", "AVAIL", "NODE", "STAT", "NODELIST"]
#             # pd.set_option('display.colheader_justify', 'left')
#             # d = d.style.set_properties(**{'text-align': 'left'})
#             # print (d.to_string(index = False))
#         # for node in linux_booking_hosts:
#         #     if node in np.array(query_results)[:,0]:
#         #         print (f"{node} currently in db")
#         #         sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
#         #     else:
#         #         sentence.insert(len(sentence), [node, "idle", "booking"])
#         # for node in windows_general_hosts:
#         #     if node in np.array(query_results)[:,0]:
#         #         print (f"{node} currently in db")
#         #         sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
#         #     else:
#         #         sentence.insert(len(sentence), [node, "idle", "general"])
#         # for node in windows_booking_hosts:
#         #     if node in np.array(query_results)[:,0]:
#         #         print (f"{node} currently in db")
#         #         sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
#         #     else:
#         #         sentence.insert(len(sentence), [node, "idle", "booking"])
#         # print (f"sentence: {sentence}")
#         # print ("\n", tabulate(sentence, headers=['node', 'status', 'pool'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
#         # logger.info ("\n" + tabulate(sentence, headers=['node', 'status', 'pool'], tablefmt='psql'))
                    
#     except my_connection.Error as e:
#         print (f"status query hit error\n{e}") if MyPrintCondition.fprint else 0
#         logger.error (f"status query hit error\n{e}")
        
        
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