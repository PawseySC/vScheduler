from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.config import Config
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.modules.cluster.os_type import find_os

who_records = CaptureLog("who", __file__)
logger = who_records.log_agent("cluster")
config = Config()

def who(node: str) -> str:
    """
    Returns who is logged in each node
    """
    my_connection = MyNode.connect_node(node)
    node_os = find_os(node)
    print (f"node_os=> {node_os}")
    users =[]
    try:

        if node_os == 'Windows':
            stdin , stdout, stderr = my_connection.exec_command("quser")
        elif node_os == 'Linux':
            # stdin , stdout, stderr = my_connection.exec_command("who")
            stdin , stdout, stderr = my_connection.exec_command("ps -eo user:30,pid,cmd | grep '[x]rdp' | awk '{print $1}' | sort -u")      # this is to get the users logged in via xrdp
        else:
            print (f"no os found for < {node} >") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            # logger_win.warning (f"no os found for < {node} >") if Config.config['partition']['windows']['node'] in node else logger_unix.warning (f"no os found for < {node} >")
            logger.warning (f"no os found for < {node} >")
            exit

        if stderr:
            print (f"Errors: {stderr.read()}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            # logger_win.error (f"Errors: {stderr.read()}") if Config.config['partition']['windows']['node'] in node else logger_unix.error (f"Errors: {stderr.read()}")
            logger.error (f"Errors: {stderr.read()}")
        for line in stdout:
            print (line.strip('\n')) if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            # logger_win.info (line.strip('\n')) if Config.config['partition']['windows']['node'] in node else logger_unix.info (line.strip('\n'))
            logger.info (line.strip('\n'))
            if not line.split()[0] in config.get("ssh.exception"):
                users.append(line.split()[0])
            else:
                continue
        my_connection.close()
        return users

    except:
        print (f"could not connect to < {node} > to query user") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        # logger_win.error (f"could not connect to < {node} > to query user") if Config.config['partition']['windows']['node'] in node else logger_unix.error (f"could not connect to < {node} > to query user")
        logger.error (f"could not connect to < {node} > to query user")