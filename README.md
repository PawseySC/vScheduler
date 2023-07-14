**Visualisation Scheduler - Pawsey Supercomputing Centre**
-----------------------------------------------------------

Apply below *Pre-setup* instruction for client-server communication and *Setup* step for vscheduler in `SQL` branch (`API` version to be developed).


## Pre-setup

1. Leave `vscheduler/socket/mgmt*.py` files in management instance and add `vscheduler/socket/vis*.py` files to each vis nodes.

2. Have `vscheduler/socket/*server.py` run as a service on management and vis instances; leave ip as blank and make sure those have different ports.

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
pip install --user virtualenv && PATH=$PATH:$HOME/.local/bin    # it's a good practice to have PATH in .bashrc
virtualenv vs                           
# OR 
sudo apt install python3-virtualenv
python -m venv vs
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
```
It's a good practice to source virtual environment in `.bashrc`.

2. Set all parameters in `lib/config.py`

3. Enjoy the code! By having virtual environment activated, run `vmanage`, `vsync`, `vquota`, `valloc`, `vinfo`, `vreport`, `vcontrol`, `vkill` commands. For more info, run any of these commands with `-h`.