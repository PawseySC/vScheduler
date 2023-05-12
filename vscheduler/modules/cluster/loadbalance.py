# allocates least busy node to general pool conection group
import multiprocessing, click
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.usage import cpu
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guacausergroup import guacamole_user_group
from vscheduler.modules.guaca.checkgroup import check_group
from vscheduler.modules.guaca.update import update
from vscheduler.modules.guaca.connperm import connection_permission
import numpy as np


x = np.zeros((2,2))
for i in range (MyCredentials.range[0], MyCredentials.range[1]):
    node = MyCredentials.node_name + '0' + str(i) if i <= 9 else MyCredentials.node_name + str(i)
    if cpu(node):
        if i == 1:
            x = [[node, cpu(node)]]
        else:
            x = np.append(x, [[node, cpu(node)]], axis = 0)
    else:
        if i == 1:
            x = [[node, '0']]
        else:
            x = np.append(x, [[node, '0']], axis = 0)
print (x)
y = x[x[:, 1].argsort()]
print (y)

node_entity = entity(y[len(y)-1, 0])        
node_group = guacamole_user_group(node_entity[0][0])
pool_entity = entity(MyCredentials.pool)
pool_group = guacamole_user_group(pool_entity[0][0])

print('node_entity',node_entity)
print('pool_entity',pool_entity)
connection_permission(node_entity[0][1], pool_entity[0][0])