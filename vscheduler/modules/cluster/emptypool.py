# allocates least busy node to general pool conection group
# import multiprocessing, click
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


def empty(node, user):
    print ("node, user=>", node, user)
    node_entity = entity(node)
    # node_group = guacamole_user_group(node_entity[0][0])
    pool_entity = entity(MyCredentials.pool)
    # pool_group = guacamole_user_group(pool_entity[0][0])

    print('node_entity', node_entity) #if MyPrintCondition.fprint else 0
    print('pool_entity', pool_entity) #if MyPrintCondition.fprint else 0
    del_connection(node_entity[0][1], pool_entity[0][0])