# get remote node usage info
from vscheduler.log.log import Capture_log
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.os_type import find_os

pool_records = Capture_log("pool", __file__)
logger_win = pool_records.log_agent("windows")
logger_unix = pool_records.log_agent("linux")


def std_print(stdin, stdout, stderr, remove, node):
    stdout_copy = []
    if stderr:
        print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
        logger_win.error (f"Errors: {stderr.read()}") if MyCredentials.windows_node_name in node else logger_unix.error (f"Errors: {stderr.read()}")
    for line in stdout:
        print (line.strip('\n')) if MyPrintCondition.fprint else 0
        logger_win.info (line.strip('\n')) if MyCredentials.windows_node_name in node else logger_unix.info (line.strip('\n'))
        stdout_copy = str(line.strip('\n')).replace("Available Physical Memory: ",'') if remove == "avail" else str(line.strip('\n')).replace("Total Physical Memory:     ",'')
        stdout_copy = stdout_copy.replace("\r",'')
    return stdout_copy


def mem(node):
    connection = MyNode.connect_node(node)
    node_os = find_os(node)
    try:
        if node_os == 'Windows':
            # wmic ComputerSystem get TotalPhysicalMemory
            # wmic OS get FreePhysicalMemory
            stdin_query , stdout_query, stderr_query = connection.exec_command('systeminfo | findstr /C:"Total Physical Memory"')        
            stdout_query_copy_total_mem = std_print(stdin_query, stdout_query, stderr_query, "total", node)
            # print (stdout_query_copy_total_mem)
            
            stdin_query , stdout_query, stderr_query = connection.exec_command('systeminfo | find "Available Physical Memory"')        
            stdout_query_copy_avail_mem = std_print(stdin_query, stdout_query, stderr_query, "avail", node)
            # print (stdout_query_copy_avail_mem)
            
            return (stdout_query_copy_avail_mem, stdout_query_copy_total_mem)
        elif node_os == 'Linux':
            stdin_query , stdout_query, stderr_query = connection.exec_command("free -h")        
            stdout_query_copy = std_print(stdin_query, stdout_query, stderr_query)
            print (f"stdout_query_copy[1][3], stdout_query_copy[1][1]: {stdout_query_copy[1][3]}, {stdout_query_copy[1][1]}") if MyPrintCondition.fprint else 0
            logger_win.info (f"stdout_query_copy[1][3], stdout_query_copy[1][1]: {stdout_query_copy[1][3]}, {stdout_query_copy[1][1]}") if MyCredentials.windows_node_name in node else logger_unix.info (f"stdout_query_copy[1][3], stdout_query_copy[1][1]: {stdout_query_copy[1][3]}, {stdout_query_copy[1][1]}")
            return (stdout_query_copy[1][3], stdout_query_copy[1][1])
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.warning (f"no os found for < {node} >")
            exit
        connection.close()
    except:
        print (f"Could not connect to ndoe < {node} > to query memory usage") if MyPrintCondition.fprint else 0
        logger_win.error (f"Could not connect to ndoe < {node} > to query memory usage") if MyCredentials.windows_node_name in node else logger_unix.error (f"Could not connect to ndoe < {node} > to query memory usage")


def cpu(node):
    connection = MyNode.connect_node(node)
    node_os = find_os(node)
    cpu_usage = ""
    count = 0
    try:
        if node_os == 'Windows':
            stdin_query , stdout_query, stderr_query = connection.exec_command('wmic cpu get loadpercentage')        
            # print (stdout_query[1].strip('\n'))
            for line in stdout_query:
                count = count + 1
                # print (line.strip('\n'))
                if count == 2:
                    cpu_usage = line.strip('\n')
                # if "LoadPercentage" not in line.strip('\n') and "100" not in line.strip('\n'):
                #     cpu_usage = line.strip('\n')
            # print (str(cpu_usage))
            return cpu_usage
        elif node_os == 'Linux':
            stdin_query , stdout_query, stderr_query = connection.exec_command('mpstat | grep idle -A 1')  
            for line in stdout_query:
                if line.split()[11] != '%idle':
                    return (line.split()[11])
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.warning (f"no os found for < {node} >")
            exit
        connection.close()
    except:
        print (f"Could not connect to ndoe < {node} > to query cpu usage") if MyPrintCondition.fprint else 0
        logger_win.error (f"Could not connect to ndoe < {node} > to query cpu usage") if MyCredentials.windows_node_name in node else logger_unix.error (f"Could not connect to ndoe < {node} > to query cpu usage")


def gpu(node):
    connection = MyNode.connect_node(node)
    node_os = find_os(node)
    gpu_model = ""
    count = 0
    try:
        if node_os == 'Windows':
            stdin_query , stdout_query, stderr_query = connection.exec_command('wmic path win32_VideoController get name')        
            # print (stdout_query[1].strip('\n'))
            for line in stdout_query:
                # print (line.strip('\n'))
                # count = count + 1
                # print (line.strip('\n'))
                # if count == 3:
                # if line.strip('\n') and "Microsoft" not in line.strip('\n'):
                if "Name" not in line.strip('\n') and "Microsoft" not in line.strip('\n'):
                    gpu_model = line.strip('\n')
                    break
            # print (str(gpu_model))
            return gpu_model
        elif node_os == 'Linux':
            stdin_query , stdout_query, stderr_query = connection.exec_command('lshw -C display')        
            return stdout_query[1][3]   # this needs to be like above
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.warning (f"no os found for < {node} >")
            exit
        connection.close()
    except:
        print (f"Could not connect to ndoe < {node} > to query cpu usage") if MyPrintCondition.fprint else 0
        logger_win.error (f"Could not connect to ndoe < {node} > to query cpu usage") if MyCredentials.windows_node_name in node else logger_unix.error (f"Could not connect to ndoe < {node} > to query cpu usage")