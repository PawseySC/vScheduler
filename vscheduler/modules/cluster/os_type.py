from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Config
from vscheduler.lib.ssh import Node as MyNode

ostype_records = CaptureLog("ostype", __file__)
logger = ostype_records.log_agent("cluster")
config = Config()

def find_os(node):
    """
    Finds os of remote node
    """
    my_connection = MyNode.connect_node(node)

    if config.get("partition.windows.node") in node:
        command = 'python -c "import platform; print (platform.uname()[0])"'
    else:
        command = 'python3 -c "import platform; print (platform.uname()[0])"'
        
    try:
        operating_system = ""
        
        # stdin , stdout, stderr = my_connection.exec_command("ver")
        # if stderr:
        #     print (f"Errors (Windows): {stderr.read()}") if MyPrintCondition.fprint else 0
        #     logger.error (f"Errors (Windows): {stderr.read()}")
        stdin , stdout, stderr = my_connection.exec_command(command)
        if stderr:
            print (f"Errors: {stderr.read()}") if MyPrintCondition.fprint else 0
            # logger_win.error (f"Errors: {stderr.read()}")
            # logger_unix.error (f"Errors: {stderr.read()}")
            logger.error (f"Errors: {stderr.read()}")
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            # logger_win.info (line.strip('\n'))
            # logger_unix.info (line.strip('\n'))
            logger.info (line.strip('\n'))
            if "Windows" in line.split():
                operating_system = "Windows"
            else:
                continue
        
        
        # stdin , stdout, stderr = my_connection.exec_command("uname")
        # if stderr:
        #     print (f"Errors (Linux): {stderr.read()}") if MyPrintCondition.fprint else 0
        #     logger.error (f"Errors (Linux): {stderr.read()}")
        # for line in stdout:
        #     print (line.strip('\n')) if MyPrintCondition.fprint else 0
        #     logger.info (line.strip('\n'))
        #     if "Linux" in line.split():
        #         operating_system = "Linux"
        #     else:
        #         continue
        my_connection.close()
        return operating_system

    except:
        print (f"could not connect to < {node} > to query os type") if MyPrintCondition.fprint else 0
        # logger_win.error (f"could not connect to < {node} > to query os type") if Config.config['partition']['windows']['node'] in node else logger_unix.error (f"could not connect to < {node} > to query os type")
        logger.error (f"could not connect to < {node} > to query os type")