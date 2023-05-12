# returns who's logged in each node
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.node import Node as MyNode
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.cluster.ostype import find_os


def who(node: str) -> str:
    my_connection = MyNode.connect_node(node)
    node_os = find_os(node)
    users =[]
    try:

        if node_os == 'Windows':
            stdin , stdout, stderr = my_connection.exec_command("quser")
        elif node_os == 'Linux':
            stdin , stdout, stderr = my_connection.exec_command("who")
        else:
            print (f"no os found for <", node, ">") if MyPrintCondition.fprint else 0
            exit

        if stderr:
            print("Errors:",stderr.read()) if MyPrintCondition.fprint else 0
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            if not line.split()[0] in MyCredentials.exception:
                users.append(line.split()[0])
            else:
                continue
        my_connection.close()
        return users

    except:
        print (f"could not connect to <", node, "> to query user") if MyPrintCondition.fprint else 0