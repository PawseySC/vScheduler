# refreshes pool member
from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.lib import config
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.cluster.load_balance import loadbalance
from vscheduler.modules.guaca.fill_pool import fillup as fill_up
from vscheduler.socket.mgmt_client import client_statistics as data_agent
from vscheduler.socket.mgmt_server import generate_general_partition_hosts

my_connection = MyDatabase.connect_guaca_db()
socket_records = CaptureLog("socket", __file__)
logger_win = socket_records.log_agent("windows")
logger_unix = socket_records.log_agent("linux")

def refresh (node):
    '''
    By setting status of a node as out of order with vset --status
    it calls this module to double check if that node is a general pool
    member to remove and replace it with another node depending on node 
    balance being ON or OFF in the config.
    '''
    os = "windows" if config.partition['windows']['node'] in node else "linux"
    print (f"osososos = {os}")
    # find the current pool member identity in guacamole db
    pool_entity = entity(config.partition['windows']['general']['pool']) if config.partition['windows']['node'] in node else entity(config.partition['linux']['general']['pool'])
    
    # find the node identity in guacamole db
    connection = f"SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_name = '{node}'"
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as cursor:
        cursor.execute(connection)
        connection_results = cursor.fetchall()
    print (connection_results)
    # is it same as out of order node? if Yes -> change the pool member
    check = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{pool_entity[0][0]}'"                      # check if pool has any connection
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as cursor:
        cursor.execute(check)
        check_results = cursor.fetchall()
    if len(check_results) > 0 and check_results[0][0] == connection_results[0][0]:
        hosts = generate_general_partition_hosts (os, node)
        logger_win.info (f"hosts: {hosts}") if os == "windows" else logger_unix.info (f"hosts: {hosts}")
        # fill up pool by new member
        # load balance ON -> call mgmt_client to collect usage data from vis nodes to rank those for loadbalance

        logger_win.info ("load balance/pool fill up") if os == "windows" else logger_unix.info ("load balance/pool fill up")
        if config.load['balance']:
            logger_win.warning ("load_balance = TRUE") if os == "windows" else logger_unix.warning ("load_balance = TRUE")
            usage_data = data_agent(hosts, os)
            logger_win.info (f"Usage data obtained from accessible nodes: {usage_data}") if os == "windows" else logger_unix.info (f"Usage data obtained from accessible nodes: {usage_data}")
            logger_win.info (f"{os} nodes load balancing in < {config.partition['windows']['general']['pool']} >") if os == "windows" else logger_unix.info (f"{os} nodes load balancing in < {config.partition['linux']['general']['pool']} >")
            loadbalance(usage_data, config.partition['linux']['general']['pool']) if os == "linux" else loadbalance(usage_data, config.partition['windows']['general']['pool'])
        # load balance OFF -> fill up pool with next node in order
        else:
            logger_win.warning ("load_balance = FALSE") if os == "windows" else logger_unix.warning ("load_balance = FALSE")
            fill_up(node, hosts)
    else:
        print (f"< {node} > was not in the pool, so no change in pool happened") if MyPrintCondition.fprint else 0
        logger_win.info (f"< {node} > was not in the pool, so no change in pool happened") if os == "windows" else logger_unix.info (f"< {node} > was not in the pool, so no change in pool happened")    