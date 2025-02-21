from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Config
from vscheduler.general.alert import mailFunction
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.update import update
from vscheduler.modules.guaca.insert import insert
from vscheduler.modules.guaca.guaca_user_group import guacamole_user_group

revert_user_records = CaptureLog("revert user", __file__)
logger = revert_user_records.log_agent("guaca")


def revert_back_to_pool(user, node, pool):
    """
    Reverts user to general partition of pool at logout
    """
    pool_entity = entity(pool)
    logger.info (f"pool_entity of < {pool} >: < {pool_entity} >")
    if pool_entity is not None:
        pool_group = guacamole_user_group(pool_entity[0][0])
    else:
        mailFunction("NoneType error",f"NoneType object is not subscriptable\nvscheduler > modules > guaca > revertuser > revert (line 17)\npool_group = guacamole_user_group({pool_entity}) = {guacamole_user_group(pool_entity[0][0])}", "", "")
        logger.critical (f"NoneType object is not subscriptable\nvscheduler > modules > guaca > revertuser > revert (line 17)\npool_group = guacamole_user_group({pool_entity}) = {guacamole_user_group(pool_entity[0][0])}")
        pass

    user_entity = entity(user)
    logger.info (f"pool_group of < {pool} >: < {pool_group} >")
    logger.info (f"user_entity of < {user} >: < {user_entity} >")
    update(user_entity[0][0], guacamole_user_group(entity(node)[0][0])[0][0], pool_group[0][0], "revert", pool)

# def insert_new_to_pool(user, pool):
#     pool_entity = entity(pool)
#     logger.info (f"pool_entity of < {pool} >: < {pool_entity} >")
#     if pool_entity is not None:
#         pool_group = guacamole_user_group(pool_entity[0][0])
#     else:
#         mailFunction("NoneType error",f"NoneType object is not subscriptable\nvscheduler > modules > guaca > revertuser > revert (line 32)\npool_group = guacamole_user_group({pool_entity}) = {pool_group}", "", "")
#         logger.critical (f"NoneType object is not subscriptable\nvscheduler > modules > guaca > revertuser > revert (line 32)\npool_group = guacamole_user_group({pool_entity}) = {pool_group}")
#         pass

#     user_entity = entity(user)
#     logger.info (f"pool_group of < {pool} >: < {pool_group} >")
#     logger.info (f"user_entity of < {user} >: < {user_entity} >")
#     insert(user_entity[0][0], pool_group[0][0])

# def insert_new_to_pool(user):
#     pool_entity = entity(MyCredentials.linux_pool)
#     logger_unix.info (f"pool_entity: {pool_entity}")
#     if pool_entity is not None:
#         pool_group = guacamole_user_group(pool_entity[0][0])
#     else:
#         mailFunction("NoneType error",f"NoneType object is not subscriptable\nvscheduler > modules > cluster > revertuser > revert (line 16)\npool_group = guacamole_user_group({pool_entity}) = {pool_group}", "", "")
#         logger_unix.critical (f"NoneType object is not subscriptable\nvscheduler > modules > cluster > revertuser > revert (line 16)\npool_group = guacamole_user_group({pool_entity}) = {pool_group}")
#         pass

#     user_entity = entity(user)
#     logger_unix.info (f"pool_entity: {pool_entity}")
#     logger_unix.info (f"pool_group: {pool_group}")
#     logger_unix.info (f"user_entity: {user_entity}")
#     insert(user_entity[0][0], pool_group[0][0])