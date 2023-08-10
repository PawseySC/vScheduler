# find os of remote node
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.ssh import Node as MyNode

records = Capture_log("booking/pool", __file__)
logger = records.log_agent()

def find_os(node):
    my_connection = MyNode.connect_node(node)

    try:
        operating_system = ""
        
        stdin , stdout, stderr = my_connection.exec_command("ver")
        if stderr:
            print ("Errors (Windows):",stderr.read()) if MyPrintCondition.fprint else 0
            logger.error ("Errors (Windows):",stderr.read())
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            logger.info (line.strip('\n'))
            if "Windows" in line.split():
                operating_system = "Windows"
            else:
                continue
        
        stdin , stdout, stderr = my_connection.exec_command("uname")
        if stderr:
            print ("Errors (Linux):",stderr.read()) if MyPrintCondition.fprint else 0
            logger.error ("Errors (Linux):",stderr.read())
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            logger.info (line.strip('\n'))
            if "Linux" in line.split():
                operating_system = "Linux"
            else:
                continue
        my_connection.close()
        return operating_system

    except:
        print (f"could not connect to < {node} > to query os type") if MyPrintCondition.fprint else 0
        logger.error (f"could not connect to < {node} > to query os type")