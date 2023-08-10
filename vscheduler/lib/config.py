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

    # local pub key location for ssh into Nebula nodes
    home = str(Path.home()) 
    ssh_username = 'admin'              # destination node admin
    key = 'id_rsa'                      # management instance private ssh key associated with public key authorized in destination nodes
    ssh_key = f'{home}/.ssh/{key}'

    # max allowed booking time and session wall time for general pool in hours
    booking_session = 24
    general_pool_wall_time = 8

    # exception users list
    exception = ['admin']

    # nodes identification -> 0 will be added to nodes number 1 to 9: w01, w02, ..., w10, w11, ...
    # node_name = 'w'
    windows_node_name = 'w'
    linux_node_name = 'nid'
    # range = [1,4]
    windows_booking = True
    windows_general = False
    windows_booking_range = [1,4]
    windows_general_range = [4,7]
    linux_booking = False
    linux_general = True
    linux_booking_range = [1,4]
    linux_general_range = [4,7]
    pool = 'pool'                       # name of general pool connection group in guacamole
    domain = 'example.domain'           # e.g.: w01.example.domain

    # notifications sent by email
    email_from = 'noreply@example.domain'
    email_to = 'username@example.domain'
    email_server = '127.0.0.1'

    # Log level: INFO, DEBUG, WARNING, ERROR, CRITICAL
    log_level = 'INFO'
    
    # load balance; if False, it allocates nodes in order to the pool, if True, allocation model applies. 
    load_balance = False