# checks rdp port via telnet connection periodically (ports 3389) to remove zombie node from being a general pool member upon unsuccessful telnet query by flagging that in report db
import time, asyncio
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.modules.guaca.pool_refresh import refresh
from vscheduler.modules.guaca.entity import entity

my_connection = MyDatabase.connect_report_db()
socket_records = Capture_log("socket", __file__)
logger_win = socket_records.log_agent("windows")
logger_unix = socket_records.log_agent("linux")


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
    pool_entity = entity(MyCredentials.windows_pool) if MyCredentials.windows_node_name in node else entity(MyCredentials.linux_pool)
    node = pool_entity[0][1]
        
    # if MyCredentials.linux_node_name:
    #     host = MyCredentials.linux_node_name + "0" + int(node.removeprefix(MyCredentials.linux_node_name)) if int(node.removeprefix(MyCredentials.linux_node_name)) < 10 else  MyCredentials.linux_node_name + int(node.removeprefix(MyCredentials.linux_node_name))
    # else:
    #     host = MyCredentials.windows_node_name + "0" + int(node.removeprefix(MyCredentials.windows_node_name)) if int(node.removeprefix(MyCredentials.windows_node_name)) < 10 else  MyCredentials.windows_node_name + int(node.removeprefix(MyCredentials.windows_node_name))
    host = node + MyCredentials.domain
    poke_result = wait_host_port(host, 3389)
    logger_unix.info (f"async result: {poke_result}") if MyCredentials.linux_node_name in node else logger_win.info (f"async result: {poke_result}")
    logger_unix.critical (f"< {node} > could not be reached on port < 3389 >") if MyCredentials.linux_node_name in node and not poke_result else logger_win.info (f"< {node} > could not be reached on port < 3389 >")
    refresh(node) if not poke_result else 0  # refresh pool if connection to pool member fails
    
if __name__ == '__main__':
    check_zombie()