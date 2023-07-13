# reverts user to general pool at logout
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guacausergroup import guacamole_user_group
from vscheduler.modules.guaca.update import update

def revert(user):
    pool_entity = entity(MyCredentials.pool)
    pool_group = guacamole_user_group(pool_entity[0][0])

    user_entity = entity(user)
    print ("pool_entity=>", pool_entity)
    print ("pool_group=>", pool_group)
    print ("user_entity=>", user_entity)
    update(user_entity[0][0], pool_group[0][0])

# if __name__ == "__main__":
#     revert()