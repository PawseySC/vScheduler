# find os of remote node
from vscheduler.log.log import CaptureLog
from vscheduler.lib import config
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.ssh import Node as MyNode

records = CaptureLog("booking/pool", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")

def find_os(node):
    my_connection = MyNode.connect_node(node)

    if config.partition['windows']['node'] in node:
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
            logger_win.error (f"Errors: {stderr.read()}")
            logger_unix.error (f"Errors: {stderr.read()}")
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            logger_win.info (line.strip('\n'))
            logger_unix.info (line.strip('\n'))
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
        logger_win.error (f"could not connect to < {node} > to query os type") if config.partition['windows']['node'] in node else logger_unix.error (f"could not connect to < {node} > to query os type")