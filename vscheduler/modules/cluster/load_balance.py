# allocates least busy node to general pool conection group
import multiprocessing, click
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
# from vscheduler.modules.cluster.usage import cpu
from vscheduler.modules.cluster.who import who
from vscheduler.modules.guaca.entity import entity
# from vscheduler.modules.guaca.guacausergroup import guacamole_user_group
# from vscheduler.modules.guaca.checkgroup import check_group
# from vscheduler.modules.guaca.update import update
from vscheduler.modules.guaca.conn_permission import connection_permission
# import numpy as np

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def loadbalance(usage_data):
    # x = {}
    # for i in range (MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
    #     node = MyCredentials.linux_node_name + '0' + str(i) if i <= 9 else MyCredentials.linux_node_name + str(i)
        # if cpu(node):
        #     if i == 1:
        #         x = [[node, cpu(node), len(who(node))]]
        #     else:
        #         x = np.append(x, [[node, cpu(node), len(who(node))]], axis = 0)
        # else:
        #     if i == 1:
        #         x = [[node, '0', len(who(node))]]
        #     else:
        #         x = np.append(x, [[node, '0', len(who(node))]], axis = 0)
    #     x[node] = [0, len(who(node))]
        
    # print (x) if MyPrintCondition.fprint else 0
    # y = x[x[:, 2].argsort()]            # 1 -> sort based on cpu usage, 2 -> sort based on number of connections; sorts in ascending order
    # y = dict(sorted(x.items(), key=lambda item: item[1]))
    # print ("sorted as:\n", y) if MyPrintCondition.fprint else 0
    sorted_usage_data = dict(sorted(usage_data.items(), key=lambda item: item[1], reverse=True))
    logger.info (f"sorted usage_data: {sorted_usage_data}")
    logger.info (f"list(sorted_usage_data.values())[0][0]=> {list(sorted_usage_data.values())[0][0]}")
    # print ("list(y.keys()[0])=>", list(y.keys())[0])
    # print("list(y.values())[0][1]=>", list(y.values())[0][1])

    node_entity = entity(list(sorted_usage_data.values())[0][0])
    # node_entity = entity(list(y.keys())[0])
    # node_entity = entity(y[0, 0])        
    # node_group = guacamole_user_group(node_entity[0][0])
    pool_entity = entity(MyCredentials.pool)
    # pool_group = guacamole_user_group(pool_entity[0][0])

    logger.info (f"node_entity: {node_entity}")
    logger.info (f"pool_entity: {pool_entity}")
    connection_permission(node_entity[0][1], pool_entity[0][0])