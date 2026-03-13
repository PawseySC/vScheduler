# established ssh connection to each node
import sys, warnings, os
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials

module_records = Capture_log("ssh", __file__)
logger_module = module_records.log_agent(f"{MyCredentials.report_windows_table}")
try:
    import paramiko
    from paramiko import SSHClient, AutoAddPolicy
except:
    print ('''
    You need paramiko module.
    https://www.paramiko.org/installing.html
    pip install paramiko\n''')
    logger_module.critical ('''
    \nYou need paramiko module.
    https://www.paramiko.org/installing.html
    pip install paramiko\n''')
    sys.exit(1)


warnings.filterwarnings(action="ignore",module=".*paramiko.*")
if os.path.isfile(MyCredentials.ssh_key):
    key = paramiko.RSAKey.from_private_key_file(MyCredentials.ssh_key)
else:
    print ("ssh key not found")
    logger_module.critical ("ssh key not found")
    exit
# key = paramiko.RSAKey.from_private_key_file(MyCredentials.ssh_key) if os.path.isfile(MyCredentials.ssh_key) else print ("ssh key not found"); logger_module.critical ("ssh key not found"); exit
user =[]

class Node:
    @staticmethod
    def connect_node(computer):
        ssh_records = Capture_log("ssh", __file__)
        logger_ssh = ssh_records.log_agent(f"{MyCredentials.report_windows_table}")
        try:
            node_name = computer + '.' + MyCredentials.domain
            node_con = paramiko.SSHClient()
            node_con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            node_con.connect(
                            hostname = node_name, 
                            username = MyCredentials.ssh_username_linux if MyCredentials.linux_node_name in computer else MyCredentials.ssh_username_windows, 
                            pkey = key, 
                            timeout=5)
            return node_con
        except:
            print (f"couldn't connect {computer} via ssh") if MyPrintCondition.fprint else 0
            logger_ssh.critical (f"couldn't connect {computer} via ssh")
            pass