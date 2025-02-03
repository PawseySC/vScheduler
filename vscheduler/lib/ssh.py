# establishes ssh connection to each node
import sys, warnings, os
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib import config

ssh_records = CaptureLog("ssh", __file__)
logger = ssh_records.log_agent("lib")

try:
    import paramiko
except:
    print ('''
    You need paramiko module.
    https://www.paramiko.org/installing.html
    pip install paramiko\n''')
    logger.critical ('''
    \nYou need paramiko module.
    https://www.paramiko.org/installing.html
    pip install paramiko\n''')
    sys.exit(1)

warnings.filterwarnings(action="ignore",module=".*paramiko.*")
if os.path.isfile(config.ssh['key']):
    key = paramiko.RSAKey.from_private_key_file(config.ssh['key'])
else:
    print ("ssh key not found")
    logger.critical ("ssh key not found")
    exit

class Node:
    @staticmethod
    def connect_node(computer):
        try:
            node_name = computer + '.' + config.email['domain']
            node_conn = paramiko.SSHClient()
            node_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            node_conn.connect(
                            hostname = node_name, 
                            username = config.ssh['user'],
                            pkey = key, 
                            timeout=5)
            return node_conn
        except paramiko.SSHException as e:
            print (f"couldn't connect {computer} via ssh\n{e}") if PrintCondition.fprint else 0
            logger.critical (f"couldn't connect {computer} via ssh\n{e}")
            pass