from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Config
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.modules.cluster.os_type import find_os

pool_records = CaptureLog("session", __file__)
logger = pool_records.log_agent("cluster")


def session(node: str, user) -> str:
    """
    Returns users sessions in remote node
    """
    my_connection = MyNode.connect_node(node)
    node_os = find_os(node)
    try:
        if node_os == 'Windows':
            stdin , stdout, stderr = my_connection.exec_command("quser")
        elif node_os == 'Linux':
            stdin , stdout, stderr = my_connection.exec_command("last -aiF -n 1 %s | awk '{gsub(/\(|\)/, \"\", $14); print $14}' | awk -F'[:+]' 'length($0) != 0 {if(length($3) == 0) {$3=$2; $2=$1; $1=0} {print ($1 * 86400) + ($2 * 3600) + ($3 * 60)}}'" % user)
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            # logger_win.warning (f"no os found for < {node} >") if Config.config['partition']['windows']['node'] in node else logger_unix.warning (f"no os found for < {node} >")
            logger.warning (f"no os found for < {node} >")
            exit

        if stderr:
            print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
            # logger_win.error (f"Errors: {stderr.read()}") if Config.config['partition']['windows']['node'] in node else logger_unix.error (f"Errors: {stderr.read()}")
            logger.error (f"Errors: {stderr.read()}")
        for line in stdout:
            second = line.strip('\n')
            print (f"second: {second}") if MyPrintCondition.fprint else 0
            # logger_win.info (f"second: {second}") if Config.config['partition']['windows']['node'] in node else logger_unix.info (f"second: {second}")
            logger.info (f"second: {second}")
        my_connection.close()
        return second

    except:
        print (f"could not connect to < {node} > to query user session time") if MyPrintCondition.fprint else 0
        # logger_win.error (f"could not connect to < {node} > to query user session time") if Config.config['partition']['windows']['node'] in node else logger_unix.error (f"could not connect to < {node} > to query user session time")
        logger.error (f"could not connect to < {node} > to query user session time")