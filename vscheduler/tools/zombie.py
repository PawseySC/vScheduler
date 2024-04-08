# checks rdp port via telnet connection periodically (ports 3389) to remove zombie node from being a general pool member upon unsuccessful telnet query by flagging that in report db
import time, asyncio
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.modules.guaca.pool_refresh import refresh
from vscheduler.modules.guaca.entity import entity
from vscheduler.general.alert import mailFunction

my_connection = MyDatabase.connect_guaca_db()
socket_records = Capture_log("zombie", __file__)
logger_zombie = socket_records.log_agent("zombie")


async def wait_host_port(host, port, duration=10, delay=2):
    """Repeatedly try if a port on a host is open until duration seconds passed
    
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
            _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=5)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            if delay:
                await asyncio.sleep(delay)
    return False


def check_zombie():
    port = MyCredentials.rdp_port
    linux_pool_entity = entity(MyCredentials.linux_pool)
    windows_pool_entity = entity(MyCredentials.windows_pool)    
    
    linux_pool_member = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{linux_pool_entity[0][0]}'"               # check the linux pool member
    windows_pool_member = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{windows_pool_entity[0][0]}'"           # check the linux pool member
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as cursor:
        cursor.execute(linux_pool_member)
        linux_pool_member_results = cursor.fetchall()
        cursor.execute(windows_pool_member)
        windows_pool_member_results = cursor.fetchall()
    
    linux_connection = f"SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_id = '{linux_pool_member_results[0][0]}'"
    windows_connection = f"SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_id = '{windows_pool_member_results[0][0]}'"
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as cursor:
        cursor.execute(linux_connection)
        linux_connection_results = cursor.fetchall()
        cursor.execute(windows_connection)
        windows_connection_results = cursor.fetchall()
    
    linux_node = linux_connection_results[0][1]
    windows_node = windows_connection_results[0][1]
    linux_host = linux_node + "." + MyCredentials.domain
    windows_host = windows_node + "." + MyCredentials.domain
    
    linux_poke_result = asyncio.run(wait_host_port(linux_host, port))
    windows_poke_result = asyncio.run(wait_host_port(windows_host, port))
    
    logger_zombie.info (f"\n< {linux_pool_entity[0][1]} > async result: {linux_poke_result}\n< {windows_pool_entity[0][1]} > async result: {windows_poke_result}")
    if not linux_poke_result:
        logger_zombie.critical (f"< {linux_node} > could not be reached on port < {port} >")  
        refresh (linux_node)        # refresh pool if connection to pool member fails
        mailFunction(f"{linux_node} <-> {port}", f"< {linux_node} > could not be reached on port < {port} >", "", "")
    else:
        logger_zombie.info (f"< {linux_node} > is reachable on port < {port} >")
        
    if not windows_poke_result:
        logger_zombie.critical (f"< {windows_node} > could not be reached on port < {port} >")
        refresh (windows_node)      # refresh pool if connection to pool member fails
        mailFunction(f"{windows_node} <-> {port}", f"< {windows_node} > could not be reached on port < {port} >", "", "")  
    else:
        logger_zombie.info (f"< {windows_node} > is reachable on port < {port} >")
    
        
if __name__ == '__main__':
    if MyCredentials.async_mode:
        check_zombie()