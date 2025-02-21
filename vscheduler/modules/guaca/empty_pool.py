from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.general.alert import mailFunction
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.conn_permission import del_connection

emptypool_records = CaptureLog("emptypool", __file__)
logger = emptypool_records.log_agent("guaca")

def empty_pool_connection(node, user, pool):
    """
    Removes the connection from pool to be filled up again in order (modules.guaca.fill_pool) 
    or by load balancing (modules.cluster.load_balance)
    """
    # logger_win.info (f"node: < {node} >, user: < {user} >, pool: < {pool} >") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"node: < {node} >, user: < {user} >, pool: < {pool} >")
    logger.info (f"node: < {node} >, user: < {user} >, pool: < {pool} >")
    node_entity = entity(node)
    # node_group = guacamole_user_group(node_entity[0][0])
    pool_entity = entity(pool)
    # pool_group = guacamole_user_group(pool_entity[0][0])
    user_entity = entity(user)
    
    # logger_win.info (f"node_entity of < { node } >: < {node_entity} >") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"node_entity of < { node } >: < {node_entity} >")
    # logger_win.info (f"pool_entity of < { pool } >: < {pool_entity} >") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"pool_entity of < { pool } >: < {pool_entity} >")
    # logger_win.info (f"user_entity of < { user } >: < {user_entity} >") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"user_entity of < { user } >: < {user_entity} >")
    logger.info (f"node_entity of < { node } >: < {node_entity} >")
    logger.info (f"pool_entity of < { pool } >: < {pool_entity} >")
    logger.info (f"user_entity of < { user } >: < {user_entity} >")
    
    
    if node_entity is not None and pool_entity is not None:
        del_connection(node_entity[0][1], pool_entity[0][0])
    else:
        mailFunction("NoneType error",f"NoneType object is not subscriptable\nvscheduler > modules > guaca > empty_pool > empty_pool_connection > del_connection (line 30)\nnode_entity = entity({node}) = {node_entity}\npool_entity = entity({pool}) = {pool_entity}", "", "")
        # logger_win.critical (f"NoneType object is not subscriptable, node_entity is empty") if Config.config['partition']['windows']['node'] in node else logger_unix.critical (f"NoneType object is not subscriptable, node_entity is empty")
        logger.critical (f"NoneType object is not subscriptable, node_entity is empty")
        exit