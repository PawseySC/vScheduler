# establishes ssh connection to each node
import warnings, sys, os, paramiko
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.config import Config

ssh_records = CaptureLog("ssh", __file__)
logger = ssh_records.log_agent("lib")
config = Config()


warnings.filterwarnings(action="ignore",module=".*paramiko.*")
if os.path.isfile(config.get("ssh.key")):
    key = paramiko.RSAKey.from_private_key_file(config.get("ssh.key"))
else:
    logger.critical ("ssh key not found")
    sys.exit ("ssh key not found")

class Node:
    """
    Establishes ssh connection to client from management server using the dedicated key in config
    """
    @staticmethod
    def connect_node(computer):
        try:
            node_name = computer + '.' + config.get("email.domain")
            node_conn = paramiko.SSHClient()
            node_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            node_conn.connect(
                            hostname = node_name, 
                            username = config.get("ssh.user"),
                            pkey = key, 
                            timeout=5)
            return node_conn
        except paramiko.SSHException as e:
            print (f"couldn't connect < {computer} > via ssh\n{e}") if verbose.mode else 0 # if PrintCondition.fprint else 0
            logger.critical (f"couldn't connect < {computer} > via ssh\n{e}")
            pass