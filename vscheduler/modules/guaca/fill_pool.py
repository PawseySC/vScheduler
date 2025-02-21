from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.conn_permission import connection_permission

fillpool_records = CaptureLog("fillpool", __file__)
logger = fillpool_records.log_agent("guaca")


def toss(node):
    """
    Returns the list of nodes in each partition
    """
    if Config.config['partition']['windows']['node'] in node:
        current_number = int(node.replace(Config.config['partition']['windows']['node'], ""))
        # logger_win.info (f"current_number+1: {current_number+1}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"current_number+1: {current_number+1}")
        logger.info (f"current_number+1: {current_number+1}")
        if current_number+1 in range(Config.config['partition']['windows']['general']['range'][0], Config.config['partition']['windows']['general']['range'][1]+1):
            current_number +=1
            # logger_win.info (f"current_number: {current_number}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"current_number: {current_number}")
            logger.info (f"current_number: {current_number}")
        else:
            current_number = Config.config['partition']['windows']['general']['range'][0]
        new_node = Config.config['partition']['windows']['node'] + "0" + str(current_number) if current_number <= 9 else Config.config['partition']['windows']['node'] + str(current_number)

    elif Config.config['partition']['linux']['node'] in node:
        current_number = int(node.replace(Config.config['partition']['linux']['node'], ""))
        # logger_win.info (f"current_number+1: {current_number+1}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"current_number+1: {current_number+1}")
        logger.info (f"current_number+1: {current_number+1}")
        if current_number+1 in range(Config.config['partition']['linux']['general']['range'][0], Config.config['partition']['linux']['general']['range'][1]+1):
            current_number +=1
            # logger_win.info (f"current_number: {current_number}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"current_number: {current_number}")
            logger.info (f"current_number: {current_number}")
        else:
            current_number = Config.config['partition']['linux']['general']['range'][0]
        new_node = Config.config['partition']['linux']['node'] + "0" + str(current_number) if current_number <= 9 else Config.config['partition']['linux']['node'] + str(current_number)
        
    return new_node


def fillup(node, hosts):
    """
    Fills up the pool based on nodes order defined in config
    this is when load balancing if off
    """
    # logger_win.info (f"Current node in the pool is {node}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"Current node in the pool is {node}")
    logger.info (f"Current node in the pool is {node}")
    new_node = toss (node)
    if len (hosts) > 0:
        while new_node not in hosts:
            new_node = toss (new_node)
    
    pool_entity = entity(Config.config['partition']['windows']['general']['pool']) if Config.config['partition']['windows']['node'] in node else entity(Config.config['partition']['linux']['general']['pool'])

    # logger_win.info (f"New node in the pool is {new_node}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"New node in the pool is {new_node}")
    logger.info (f"New node in the pool is {new_node}")
    new_node_entity = entity(new_node)
    # logger_win.info (f"new_node_entity: {new_node_entity}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"new_node_entity: {new_node_entity}")
    logger.info (f"new_node_entity: {new_node_entity}")
    # logger_win.info (f"pool_entity: {pool_entity}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"pool_entity: {pool_entity}")
    logger.info (f"pool_entity: {pool_entity}")

    connection_permission(new_node_entity[0][1], pool_entity[0][0])