from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib import config
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.modules.cluster.os_type import find_os
from vscheduler.modules.reports.record_log_io import record_logout
from vscheduler.modules.guaca.revert_user import revert_back_to_pool

logoff_records = CaptureLog("logoff", __file__)
logger = logoff_records.log_agent("cluster")


def std_print(stdin, stdout, stderr):
    """
    Prints query results and returns copy of results
    The reason is by printing tupple, cursor sits at the end and returns empty tupple >>> **This could be optimised** <<<
    """
    stdout_copy = []
    if stderr:
        print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
        logger.error (f"Errors: {stderr.read()}")
    for line in stdout:
        print (line.strip('\n')) if MyPrintCondition.fprint else 0
        logger.info ("\n" + line.strip('\n'))
        stdout_copy.append(line)
    return stdout_copy


def logoff(user, node):
    """
    Logs off user from client node
    """
    connection = MyNode.connect_node(node)
    node_os = find_os(node)
    print (f"node os: {node_os}")
    try:
        if node_os == 'Windows':
            stdin_query , stdout_query, stderr_query = connection.exec_command("query session")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            # if any(user in x for x in stdout_query_copy):
            for line in stdout_query_copy:
                if (line.split()[0] == user or line.split()[1] == user) and user not in config.ssh['exception']:
                    if line.split()[0] == user:
                        stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command(f"logoff {line.split()[1]}")
                    elif line.split()[1] == user:
                        stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command(f"logoff {line.split()[2]}")
                    std_print(stdin_logoff, stdout_logoff, stderr_logoff)
                    print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
                    logger.info (f"session for {user} was killed on {node}")
                    if config.partition['windows']['node'] in node:
                        if int(node.removeprefix(config.partition['windows']['node'])) in range(config.partition['windows']['general']['range'][0], config.partition['windows']['general']['range'][1]+1):
                            record_logout(user, node, config.database['report']['table']['windows'], "general")
                            revert_back_to_pool(user, node, config.partition['windows']['general']['pool'])
                        elif int(node.removeprefix(config.partition['windows']['node'])) in range(config.partition['windows']['booking']['range'][0], config.partition['windows']['booking']['range'][1]+1):
                            record_logout(user, node, config.database['report']['table']['windows'], "booking")
                elif user in config.ssh['exception']:
                    print (f"{user} is exception") if MyPrintCondition.fprint else 0
                    logger.info (f"{user} is exception")
                else:
                    continue
            # else:
            #     print (f"user <", user, "> is not logged in <", node, ">") if MyPrintCondition.fprint else 0
            
        elif node_os == 'Linux':
            stdin_query , stdout_query, stderr_query = connection.exec_command("who -u")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            
            # if any(user in x for x in stdout_query_copy):
            #     for line in stdout_query_copy:
            #         if line.split()[0] == user and user not in MyCredentials.exception:
            #         # if line.split()[0] == user:
            #             stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command("sudo pkill -u %s" % (line.split()[0]))
            #             std_print(stdin_logoff, stdout_logoff, stderr_logoff)
            #             print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
            #             logger.info (f"session for {user} was killed on {node}")
            #             if config.partition['linux']['node'] in node:
            #                 if int(node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['general']['range'][0], config.partition['linux']['general']['range'][1]+1): 
            #                     record_logout(user, node, MyCredentials.report_linux_table, "general")
            #                     revert_back_to_pool(user, node, config.partition['linux']['general']['pool'])
            #                 elif int(node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['booking']['range'][0], config.partition['linux']['booking']['range'][1]+1):
            #                     record_logout(user, node, MyCredentials.report_linux_table, "booking")
            #         elif user in MyCredentials.exception:
            #             print (f"{user} is exception") if MyPrintCondition.fprint else 0
            #             logger.info (f"{user} is exception")
            #         else:
            #             continue
            # else:
            #     print (f"user < {user} > is not logged in < {node}>") if MyPrintCondition.fprint else 0
            #     logger.info (f"user < {user} > is not logged in < {node}>")
        
            stdin_logoff , stdout_logoff, stderr_logoff = connection.exec_command("sudo pkill -u %s" % (user))
            std_print(stdin_logoff, stdout_logoff, stderr_logoff)
            print (f"session for {user} was killed on {node}") if MyPrintCondition.fprint else 0
            logger.info (f"session for {user} was killed on {node}")
            if config.partition['linux']['node'] in node:
                if int(node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['general']['range'][0], config.partition['linux']['general']['range'][1]+1): 
                    record_logout(user, node, config.database['report']['table']['linux'], "general")
                    revert_back_to_pool(user, node, config.partition['linux']['general']['pool'])
                elif int(node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['booking']['range'][0], config.partition['linux']['booking']['range'][1]+1):
                    record_logout(user, node, config.database['report']['table']['linux'], "booking")
            # else:
            #     print (f"user < {user} > is not logged in < {node}>") if MyPrintCondition.fprint else 0
            #     logger.info (f"user < {user} > is not logged in < {node}>")
            
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger.warning (f"no os found for < {node} >")
            logger.warning (f"no os found for < {node} >")
            exit
        connection.close()

    except:
        print (f"Could not connect to ndoe < {node} > to query session and logoff") if MyPrintCondition.fprint else 0
        logger.error (f"Could not connect to ndoe < {node} > to query session and logoff")
        logger.error (f"Could not connect to ndoe < {node} > to query session and logoff")