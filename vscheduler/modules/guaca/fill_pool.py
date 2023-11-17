# fills up the pool based on nodes order defined in config; 
# this is when load balancing if off.
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.conn_permission import connection_permission

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def fillup(node):
    logger.info (f"Current node in the pool is {node}")
    if MyCredentials.windows_node_name in node:
        current_number = int(node.replace(MyCredentials.windows_node_name, ""))
        logger.info (f"current_number+1: {current_number+1}")
        if current_number+1 in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
            current_number +=1
            logger.info (f"current_number: {current_number}")
        else:
            current_number = MyCredentials.windows_general_range[0]
        new_node = MyCredentials.windows_node_name + "0" + str(current_number) if current_number <= 9 else MyCredentials.windows_node_name + str(current_number)
        pool_entity = entity(MyCredentials.windows_pool)

    if MyCredentials.linux_node_name in node:
        current_number = int(node.replace(MyCredentials.linux_node_name, ""))
        logger.info (f"current_number+1: {current_number+1}")
        if current_number+1 in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
            current_number +=1
            logger.info (f"current_number: {current_number}")
        else:
            current_number = MyCredentials.linux_general_range[0]
        new_node = MyCredentials.linux_node_name + "0" + str(current_number) if current_number <= 9 else MyCredentials.linux_node_name + str(current_number)
        pool_entity = entity(MyCredentials.linux_pool)

    logger.info (f"New node in the pool is {new_node}")
    new_node_entity = entity(new_node)
    logger.info (f"new_node_entity: {new_node_entity}")
    logger.info (f"pool_entity: {pool_entity}")

    connection_permission(new_node_entity[0][1], pool_entity[0][0])