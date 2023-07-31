# allocates least busy node to general pool conection group
# import multiprocessing, click
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
# from vscheduler.general.initiate import Initiation as initiate
# from vscheduler.general.initiate import PrintCondition as MyPrintCondition
# from vscheduler.modules.cluster.usage import cpu
# from vscheduler.modules.cluster.who import who
from vscheduler.modules.guaca.entity import entity
# from vscheduler.modules.guaca.guacausergroup import guacamole_user_group
# from vscheduler.modules.guaca.checkgroup import check_group
# from vscheduler.modules.guaca.update import update
from vscheduler.modules.guaca.connperm import del_connection
from vscheduler.general.alert import mailFunction

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def empty(node, user):
    logger.info (f"node: {node} , user: {user}")
    node_entity = entity(node)
    # node_group = guacamole_user_group(node_entity[0][0])
    pool_entity = entity(MyCredentials.pool)
    # pool_group = guacamole_user_group(pool_entity[0][0])

    logger.info (f"node_entity: {node_entity}") #if MyPrintCondition.fprint else 0
    logger.info (f"pool_entity: {pool_entity}") #if MyPrintCondition.fprint else 0
    
    if node_entity is not None and pool_entity is not None:
        del_connection(node_entity[0][1], pool_entity[0][0])
    else:
        mailFunction(f"NoneType error","NoneType object is not subscriptable\nvscheduler > modules > cluster > emptypool > empty > del_connection (line 27)\nnode_entity = entity({node}) = {node_entity}\npool_entity = entity({MyCredentials.pool}) = {pool_entity}", "", "")
        logger.critical (f"NoneType object is not subscriptable, node_entity is empty")
        exit