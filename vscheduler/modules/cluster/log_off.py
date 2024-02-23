# logs off user from node
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.modules.cluster.os_type import find_os

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")   # **** logger_unix needs to be added; win flag should be sent when calling the function ****

def std_print(stdin, stdout, stderr):
    stdout_copy = []
    if stderr:
        print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
        logger_win.error (f"Errors: {stderr.read()}")
    for line in stdout:
        print (line.strip('\n')) if MyPrintCondition.fprint else 0
        logger_win.info ("\n" + line.strip('\n'))
        stdout_copy.append(line)
    return stdout_copy

def logoff(user, node):
    connection = MyNode.connect_node(node)
    node_os = find_os(node)
    print (f"node os: {node_os}")
    try:
        if node_os == 'Windows':
            stdin_query , stdout_query, stderr_query = connection.exec_command("query session")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            # if any(user in x for x in stdout_query_copy):
            for line in stdout_query_copy:
                if (line.split()[0] == user or line.split()[1] == user) and user not in MyCredentials.exception:
                    if line.split()[0] == user:
                        stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command(f"logoff {line.split()[1]}")
                    elif line.split()[1] == user:
                        stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command(f"logoff {line.split()[2]}")
                    std_print(stdin_logoff, stdout_logoff, stderr_logoff)
                    print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
                    logger_win.info (f"session for {user} was killed on {node}")
                elif user in MyCredentials.exception:
                    print (f"{user} is exception") if MyPrintCondition.fprint else 0
                    logger_win.info (f"{user} is exception")
                else:
                    continue
            # else:
            #     print (f"user <", user, "> is not logged in <", node, ">") if MyPrintCondition.fprint else 0
            
        elif node_os == 'Linux':
            stdin_query , stdout_query, stderr_query = connection.exec_command("who -u")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            
            if any(user in x for x in stdout_query_copy):
                for line in stdout_query_copy:
                    if line.split()[0] == user and user not in MyCredentials.exception:
                    # if line.split()[0] == user:
                        stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command("sudo pkill -KILL -u %s" % (line.split()[0]))
                        std_print(stdin_logoff, stdout_logoff, stderr_logoff)
                        print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
                        logger_win.info (f"session for {user} was killed on {node}")
                    elif user in MyCredentials.exception:
                        print (f"{user} is exception") if MyPrintCondition.fprint else 0
                        logger_win.info (f"{user} is exception")
                    else:
                        continue
            else:
                print (f"user < {user} > is not logged in < {node}>") if MyPrintCondition.fprint else 0
                logger_win.info (f"user < {user} > is not logged in < {node}>")
            
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >")
            exit
        connection.close()

    except:
        print (f"Could not connect to ndoe < {node} > to query session and logoff") if MyPrintCondition.fprint else 0
        logger_win.error (f"Could not connect to ndoe < {node} > to query session and logoff")