# established ssh connection to each node
import sys, warnings, os
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
try:
    import paramiko
    from paramiko import SSHClient, AutoAddPolicy
except:
    print ('''
    You need paramiko module.
    https://www.paramiko.org/installing.html
    pip install paramiko\n''')
    sys.exit(1)


warnings.filterwarnings(action='ignore',module='.*paramiko.*')
key = paramiko.RSAKey.from_private_key_file(MyCredentials.ssh_key) if os.path.isfile(MyCredentials.ssh_key) else print ("ssh key not found"); exit
user =[]

class Node:
    @staticmethod
    def connect_node(computer):
        try:
            node_name = computer + '.' + MyCredentials.domain
            node_con = paramiko.SSHClient()
            node_con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            node_con.connect(
                            hostname = node_name, 
                            username = MyCredentials.ssh_username, 
                            pkey = key, 
                            timeout=5)
            return node_con
        except:
            print ("couldn't connect %s via ssh" %computer) if MyPrintCondition.fprint else 0
            pass