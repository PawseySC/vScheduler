# returns the user session in remote node in sec
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.lib import config
from vscheduler.modules.cluster.os_type import find_os

pool_records = CaptureLog("pool", __file__)
logger_win = pool_records.log_agent("windows")
logger_unix = pool_records.log_agent("linux")

def session(node: str, user) -> str:
    my_connection = MyNode.connect_node(node)
    node_os = find_os(node)
    try:
        if node_os == 'Windows':
            stdin , stdout, stderr = my_connection.exec_command("quser")
        elif node_os == 'Linux':
            stdin , stdout, stderr = my_connection.exec_command("last -aiF -n 1 %s | awk '{gsub(/\(|\)/, \"\", $14); print $14}' | awk -F'[:+]' 'length($0) != 0 {if(length($3) == 0) {$3=$2; $2=$1; $1=0} {print ($1 * 86400) + ($2 * 3600) + ($3 * 60)}}'" % user)
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if config.partition['windows']['node'] in node else logger_unix.warning (f"no os found for < {node} >")
            exit

        if stderr:
            print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
            logger_win.error (f"Errors: {stderr.read()}") if config.partition['windows']['node'] in node else logger_unix.error (f"Errors: {stderr.read()}")
        for line in stdout:
            second = line.strip('\n')
            print (f"second: {second}") if MyPrintCondition.fprint else 0
            logger_win.info (f"second: {second}") if config.partition['windows']['node'] in node else logger_unix.info (f"second: {second}")
        my_connection.close()
        return second

    except:
        print (f"could not connect to < {node} > to query user session time") if MyPrintCondition.fprint else 0
        logger_win.error (f"could not connect to < {node} > to query user session time") if config.partition['windows']['node'] in node else logger_unix.error (f"could not connect to < {node} > to query user session time")