# returns who's logged in each node
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.cluster.os_type import find_os

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")
logger_unix = booking_records.log_agent("linux")


def who(node: str) -> str:
    my_connection = MyNode.connect_node(node)
    node_os = find_os(node)
    print (f"node_os=> {node_os}")
    users =[]
    try:

        if node_os == 'Windows':
            stdin , stdout, stderr = my_connection.exec_command("quser")
        elif node_os == 'Linux':
            stdin , stdout, stderr = my_connection.exec_command("who")
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.warning (f"no os found for < {node} >")
            exit

        if stderr:
            print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
            logger_win.error (f"Errors: {stderr.read()}") if MyCredentials.windows_node_name in node else logger_unix.error (f"Errors: {stderr.read()}")
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            logger_win.info (line.strip('\n')) if MyCredentials.windows_node_name in node else logger_unix.info (line.strip('\n'))
            if not line.split()[0] in MyCredentials.exception:
                users.append(line.split()[0])
            else:
                continue
        my_connection.close()
        return users

    except:
        print (f"could not connect to < {node} > to query user") if MyPrintCondition.fprint else 0
        logger_win.error (f"could not connect to < {node} > to query user") if MyCredentials.windows_node_name in node else logger_unix.error (f"could not connect to < {node} > to query user")