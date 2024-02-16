# removes the connection from pool to be filled up again in order (modules.guaca.fill_pool) or by load balancing (modules.cluster.load_balance)
from vscheduler.log.log import Capture_log
from vscheduler.general.alert import mailFunction
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.conn_permission import del_connection

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def empty_pool_connection(node, user, pool):
    logger.info (f"node: < {node} >, user: < {user} >, pool: < {pool} >")
    node_entity = entity(node)
    # node_group = guacamole_user_group(node_entity[0][0])
    pool_entity = entity(pool)
    # pool_group = guacamole_user_group(pool_entity[0][0])

    logger.info (f"node_entity of < { node } >: < {node_entity} >")
    logger.info (f"pool_entity of < { pool } >: < {pool_entity} >")
    
    if node_entity is not None and pool_entity is not None:
        del_connection(node_entity[0][1], pool_entity[0][0])
    else:
        mailFunction("NoneType error",f"NoneType object is not subscriptable\nvscheduler > modules > guaca > empty_pool > empty_pool_connection > del_connection (line 30)\nnode_entity = entity({node}) = {node_entity}\npool_entity = entity({pool}) = {pool_entity}", "", "")
        logger.critical (f"NoneType object is not subscriptable, node_entity is empty")
        exit