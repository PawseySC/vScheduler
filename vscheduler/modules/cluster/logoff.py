# logs off user from node
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.node import Node as MyNode
from vscheduler.modules.cluster.ostype import find_os

booking_records = Capture_log("booking", __file__)
logger = booking_records.log_agent()

def std_print(stdin, stdout, stderr):
    stdout_copy = []
    if stderr:
        print ("Errors:", stderr.read()) if MyPrintCondition.fprint else 0
        logger.error ("Errors:" + stderr.read())
    for line in stdout:
        print (line.strip('\n')) if MyPrintCondition.fprint else 0
        logger.info ("\n" + line.strip('\n'))
        stdout_copy.append(line)
    return stdout_copy

def logoff(user, node):
    connection = MyNode.connect_node(node)
    node_os = find_os(node)
    try:
        if node_os == 'Windows':
            stdin_query , stdout_query, stderr_query = connection.exec_command("query session")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            
            # if any(user in x for x in stdout_query_copy):
            for line in stdout_query_copy:
                if line.split()[0] == user and user not in MyCredentials.exception:
                    stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command("logoff %s" % (line.split()[1]))
                    std_print(stdin_logoff, stdout_logoff, stderr_logoff)
                    print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
                    logger.info (f"session for {user} was killed on {node}")
                elif user in MyCredentials.exception:
                    print (f"{user} is exception") if MyPrintCondition.fprint else 0
                    logger.info (f"{user} is exception")
                else:
                    continue
            # else:
            #     print (f"user <", user, "> is not logged in <", node, ">") if MyPrintCondition.fprint else 0
            
        elif node_os == 'Linux':
            stdin_query , stdout_query, stderr_query = connection.exec_command("who -u")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            
            if any(user in x for x in stdout_query_copy):
                for line in stdout_query_copy:
                    # if line.split()[0] == user and user not in MyCredentials.exception:
                    if line.split()[0] == user:
                        stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command("sudo pkill -KILL -u %s" % (line.split()[0]))
                        std_print(stdin_logoff, stdout_logoff, stderr_logoff)
                        print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
                        logger.info (f"session for {user} was killed on {node}")
                    else:
                        continue
            else:
                print (f"user < {user} > is not logged in < {node}>") if MyPrintCondition.fprint else 0
                logger.info (f"user < {user} > is not logged in < {node}>")
            
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger.info (f"no os found for < {node} >")
            exit
        connection.close()

    except:
        print (f"Could not connect to ndoe < {node} > to query session and logoff") if MyPrintCondition.fprint else 0
        logger.error (f"Could not connect to ndoe < {node} > to query session and logoff")