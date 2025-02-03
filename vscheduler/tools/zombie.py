# checks rdp port via telnet connection periodically (ports 3389) to remove zombie node from being a general pool member upon unsuccessful telnet query by flagging that in report db
import time, asyncio
from vscheduler.log.log import CaptureLog
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.modules.reports.status import status_update as update_status
from vscheduler.modules.guaca.pool_refresh import refresh
from vscheduler.modules.guaca.entity import entity
from vscheduler.general.alert import mailFunction

my_connection = MyDatabase.connect_guaca_db()
socket_records = CaptureLog("zombie", __file__)
logger_zombie = socket_records.log_agent("zombie")


async def wait_host_port(host, port, duration=3, delay=1):
    """
    Repeatedly try if a port on a host is open until duration seconds passed
    
    Parameters
    ----------
    host : str
        host ip address or hostname
    port : int
        port number
    duration : int, optional
        Total duration in seconds to wait, by default 10
    delay : int, optional
        delay in seconds between each try, by default 2
    
    Returns
    -------
    awaitable bool
    """
    tmax = time.time() + duration
    while time.time() < tmax:
        try:
            _reader, writer = await asyncio.wait_for(asyncio.open_connection(host + "." + MyCredentials.domain, port), timeout=5)
            writer.close()
            await writer.wait_closed()
            logger_zombie.info (f"< {host} > is reachable on port < {port} >")
            return True
        except:
            if delay:
                await asyncio.sleep(delay)
    logger_zombie.critical (f"< {host} > could not be reached on port < {port} >")  
    refresh (host)        # refresh pool if connection to pool member fails
    update_status(host, "down") # flag it in db as down
    mailFunction(f"{host} <-> {port}", f"< {host} > could not be reached on port < {port} >", "", "")
    return False

# async def foo(host, port, duration=3, delay=1):
#     tmax = time.time() + duration
#     while time.time() < tmax:
#         try:
#             _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=5)
#             writer.close()
#             await writer.wait_closed()
#             logger_zombie.info (f"< {host} > is reachable on port < {port} >")
#             print (True)
#             return True
#         except:
#             if delay:
#                 await asyncio.sleep(delay)
#     print (False)
#     return False

def check_zombie():
    port = MyCredentials.remote_port
    # linux_pool_entity = entity(MyCredentials.linux_pool)
    # windows_pool_entity = entity(MyCredentials.windows_pool)    
    
    # linux_pool_member = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{linux_pool_entity[0][0]}'"               # check the linux pool member
    # windows_pool_member = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{windows_pool_entity[0][0]}'"           # check the linux pool member
    # my_connection.ping()  # reconnecting mysql in case of connection timed out
    # with my_connection.cursor() as cursor:
    #     cursor.execute(linux_pool_member)
    #     linux_pool_member_results = cursor.fetchall()
    #     cursor.execute(windows_pool_member)
    #     windows_pool_member_results = cursor.fetchall()
    
    # linux_connection = f"SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_id = '{linux_pool_member_results[0][0]}'"
    # windows_connection = f"SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_id = '{windows_pool_member_results[0][0]}'"
    # my_connection.ping()  # reconnecting mysql in case of connection timed out
    # with my_connection.cursor() as cursor:
    #     cursor.execute(linux_connection)
    #     linux_connection_results = cursor.fetchall()
    #     cursor.execute(windows_connection)
    #     windows_connection_results = cursor.fetchall()
    
    # linux_node = linux_connection_results[0][1]
    # windows_node = windows_connection_results[0][1]
    # linux_host = linux_node + "." + MyCredentials.domain
    # windows_host = windows_node + "." + MyCredentials.domain
    
    # linux_poke_result = asyncio.run(wait_host_port(linux_host, port))
    # windows_poke_result = asyncio.run(wait_host_port(windows_host, port))
    
    linux_hosts_general = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
    linux_hosts_booking = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
    windows_hosts_general = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
    windows_hosts_booking = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1)]
    
    [asyncio.run(wait_host_port(host, port)) for host in linux_hosts_general if MyCredentials.linux_general]
    [asyncio.run(wait_host_port(host, port)) for host in linux_hosts_booking if MyCredentials.linux_booking]
    [asyncio.run(wait_host_port(host, port)) for host in windows_hosts_general if MyCredentials.windows_general]
    [asyncio.run(wait_host_port(host, port)) for host in windows_hosts_booking if MyCredentials.windows_booking]
    # asyncio.run(wait_host_port(linux_hosts_general, port)) if MyCredentials.linux_general else 0
    # asyncio.run(wait_host_port(linux_hosts_booking, port)) if MyCredentials.linux_booking else 0
    # asyncio.run(wait_host_port(windows_hosts_general, port)) if MyCredentials.windows_general else 0
    # asyncio.run(wait_host_port(windows_hosts_booking, port)) if MyCredentials.windows_booking else 0
    # asyncio.run(foo("w08.pawsey.org.au", port))
    
    # logger_zombie.info (f"\n< {linux_pool_entity[0][1]} > async result: {linux_poke_result}\n< {windows_pool_entity[0][1]} > async result: {windows_poke_result}")
    # if not linux_poke_result:
    #     logger_zombie.critical (f"< {linux_node} > could not be reached on port < {port} >")  
    #     refresh (linux_node)        # refresh pool if connection to pool member fails
    #     update_status(linux_node, "down") # flag it in db as down
    #     mailFunction(f"{linux_node} <-> {port}", f"< {linux_node} > could not be reached on port < {port} >", "", "")
    # else:
    #     logger_zombie.info (f"< {linux_node} > is reachable on port < {port} >")
        
    # if not windows_poke_result:
    #     logger_zombie.critical (f"< {windows_node} > could not be reached on port < {port} >")
    #     refresh (windows_node)      # refresh pool if connection to pool member fails
    #     update_status(windows_node, "down") # flag it in db as down
    #     mailFunction(f"{windows_node} <-> {port}", f"< {windows_node} > could not be reached on port < {port} >", "", "")  
    # else:
    #     logger_zombie.info (f"< {windows_node} > is reachable on port < {port} >")
    
        
if __name__ == '__main__':
    if MyCredentials.async_mode:
        check_zombie()