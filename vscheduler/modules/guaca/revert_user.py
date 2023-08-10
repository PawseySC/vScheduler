# reverts user to general pool at logout
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guaca_user_group import guacamole_user_group
from vscheduler.modules.guaca.update import update
from vscheduler.general.alert import mailFunction

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def revert(user):
    pool_entity = entity(MyCredentials.pool)
    logger.info (f"pool_entity: {pool_entity}")
    if pool_entity is not None:
        pool_group = guacamole_user_group(pool_entity[0][0])
    else:
        mailFunction("NoneType error",f"NoneType object is not subscriptable\nvscheduler > modules > cluster > revertuser > revert (line 16)\npool_group = guacamole_user_group({pool_entity}) = {pool_group}", "", "")
        logger.critical (f"NoneType object is not subscriptable\nvscheduler > modules > cluster > revertuser > revert (line 16)\npool_group = guacamole_user_group({pool_entity}) = {pool_group}")
        pass

    user_entity = entity(user)
    logger.info (f"pool_entity: {pool_entity}")
    logger.info (f"pool_group: {pool_group}")
    logger.info (f"user_entity: {user_entity}")
    update(user_entity[0][0], pool_group[0][0])

# if __name__ == "__main__":
#     revert()