**Visualisation Scheduler - Pawsey Supercomputing Centre**
-----------------------------------------------------------

Apply below *Pre-setup* instruction for client-server communication and *Setup* step for vscheduler in `SQL` branch (`API` version to be developed).


## Pre-setup

1. Leave `vscheduler/socket/mgmt*.py` files in management instance and add `vscheduler/socket/vis*.py` files to each vis node.

2. Have `vscheduler/socket/*server.py` run as a service on management and vis nodes; leave ip as blank and make sure those have different ports.

**For management instance:**

Create new service in `/etc/systemd/system/mgmt_socket.service` as below:
```
[Unit]
Description=mgmt_socket

[Service]
User=ubuntu
Type=simple
ExecStart=/home/ubuntu/visualisation_scheduler/vs/bin/python3 /home/ubuntu/visualisation_scheduler/vscheduler/socket/mgmt_server.py
Environment="PATH=/home/ubuntu/visualisation_scheduler/vs/bin"
Restart=always

[Install]
WantedBy=multi-user.target
```
and enable/start it:
```
systemctl daemon-reload
systemctl enable mgmt_socket.service
systemctl start mgmt_socket.service
```

**For vis nodes:**

Create new service in `/etc/systemd/system/vis_socket.service` as below:
```
[Unit]
Description=vis_socket

[Service]
User=admin
Type=simple
ExecStart=/usr/bin/python3 <FOLDER>/vis_server.py
Restart=always
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
```
and enable/start it:
```
systemctl daemon-reload
systemctl enable vis_socket.service
systemctl start vis_socket.service
```

2. Locate `vscheduler/socket/vis_client*.py` on vis nodes in `/etc/profile.d/` and set management instance (server) ip and port; For `mgmt_client.py`, set ips of all destination nodes in a list. 

3. To run the login script at each user login event in vis nodes, add below line to EOF `/etc/profile`:
```
/usr/bin/python3 /etc/profile.d/vis_client_login.py
```

4. To run the logout script at each user logout event in vis nodes, add below line to EOF `/etc/bash.bash_logout`:
```
/usr/bin/python3 /etc/profile.d/vis_client_logout.py
```

> Note: Steps 3 & 4 are for bash sessions only. For desktop sessions, you need to edit relevant desktop manager files to trigger scripts at login/out events.

5. Arrange admin access for management instance on each destination node by:
```
sudo adduser admin
sudo usermod -aG sudo admin
```
and, popoulate public key of management instance over into `~/.ssh/authorized_keys` of admin profile on each destination node for passwordless communication.


## Setup

By having [Guacamole](https://guacamole.apache.org/) and [booked](https://www.bookedscheduler.com/) installed, Python3 and pip3 are the only requirements to run the script (The script has been developed and tested based on Python 3.10.6). All required packages will be automatically installed on management instance in step 1 below.

1. Setup virtual environemt on management instance

To have the script running environment clean and isolated, install all packages in a virtual environment avoiding confliction or version incompatibility issues with other tools/packages.

```
sudo apt install python3-pip
# next install and setup virtualenv:
sudo apt install python3-virtualenv
virtualenv vs
# finally:
source vs/bin/activate
(vs) $ pip install -e .                 # run in setup.py directory to install all required pacjkages inside virtual environment
deactivate                              # to exit from virtual environment
```
Above will install follwing major packages along with their dependencies in python virtual environment:
```
- Click 8.1.3
- paramiko 3.0.0
- PyMySQL 1.0.2
- numpy 1.24.3
- tabulate 0.9.0
- rich 13.3.5
- jinja2 3.1.2
```
It's a good practice to source virtual environment in `.bashrc`.

2. Setup local MySQL database for report:
```
sudo apt install mysql-server
sudo mysql
create database report;
use report;
create table windows (
    id MEDIUMINT NOT NULL AUTO_INCREMENT,
    node VARCHAR(255),
    user VARCHAR(255),
    pool VARCHAR(255),
    start DATETIME,
    end DATETIME,
    PRIMARY KEY (id)
    );
mysql> create table linux (
    id MEDIUMINT NOT NULL AUTO_INCREMENT,
    node VARCHAR(255),
    user VARCHAR(255),
    pool VARCHAR(255),
    start DATETIME,
    end DATETIME,
    PRIMARY KEY (id)
    );
use mysql;
create user 'reporter'@'%' IDENTIFIED WITH mysql_native_password BY 'PASSWORD';
grant all privileges on report.* to 'reporter'@'%';
flush privileges;
quit
```
To access remotely, add `bind-address            = 0.0.0.0` to `sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf` and restart MySQ: server:
```
sudo systemctl restart mysql
```

3. Set all parameters in `vscheduler/lib/config.py`

4. Enjoy the code! By having virtual environment always activated (add `source vscheduler/vs/bin/activate` to _~/.bashrc_), run `vmanage`, `vsync`, `vquota`, `valloc`, `vinfo`, `vreport`, `vcontrol`, `vkill` commands. For more info, run any of these commands with `-h`.
