# configs used by all modules
import os
from pathlib import Path

class Credentials:
    # booked db credentials
    booked_host ='booked.local'
    booked_user ='booked_user'
    booked_passwd ='1234'
    booked_db ='booked_db'
    booked_port = 3306
    
    # guacamole db credentials
    guaca_host = 'guaca.local'
    guaca_user = 'guacamole_user'
    guaca_passwd = '1234'
    guaca_db = 'guacamole_db'
    guaca_port = 3306

    # report db credentials
    report_host = 'localhost'
    report_user = 'report_user'
    report_passwd = '1234'
    report_db = 'report'
    report_port = 3306
    report_windows_table = 'windows'
    report_linux_table = 'linux'
    report_status_table = 'status'
    report_exception_table = 'exception'

    # local pub key location for ssh into Nebula nodes
    home = str(Path.home()) 
    ssh_username_linux = 'admin'              # destination node admin
    ssh_username_windows = 'admin'              # destination node admin
    key = 'id_rsa'                      # management instance private ssh key associated with public key authorized in destination nodes
    ssh_key = f'{home}/.ssh/{key}'

    # max allowed booking time and session wall time for general pool in hours
    booking_session = 24
    general_pool_wall_time = 8

    # exception users list
    exception = ['admin']

    # nodes identification -> 0 will be added to nodes number 1 to 9: w01, w02, ..., w10, w11, ...
    windows_node_name = 'windows'
    linux_node_name = 'linux'
    windows_booking = False
    windows_general = False
    windows_booking_range = [1,4]
    windows_general_range = [4,7]
    linux_booking = False
    linux_general = True
    linux_booking_range = [1,4]
    linux_general_range = [27,28]
    linux_pool = 'linux'              # name of general pool connection group in guacamole for linux machines
    windows_pool = 'windows'             # name of general pool connection group in guacamole for windows machines
    domain = 'example.domain'           # e.g.: w01.example.domain

    # notifications sent by email
    email_from = 'noreply@example.domain'
    email_to = 'username@example.domain'
    email_server = '127.0.0.1'

    # Log level: INFO, DEBUG, WARNING, ERROR, CRITICAL
    log_level = 'INFO'
    
    # load balance; if False, it allocates nodes in order to the pool, if True, allocation model applies. 
    load_balance = False
        
    # set to True to acyivate checking xrdp connection for finding zombie nodes 
    async_mode = True
    
    # the port rdp/vnc connects
    rdp_port = 3389