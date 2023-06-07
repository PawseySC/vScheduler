**Visualisation Scheduler - Pawsey Supercomputing Centre**
-----------------------------------------------------------

Apply below *Pres-setup* instruction for client-server communication and *Setup* step for vscheduler in `SQL` branch; `API` version to be developed.


## Pre-setup

1. Locate `socket/mgmt*.py` files in management instance and `socket/comp*.py` files in each compute/vis nodes.

2. Have `socket/*server.py` run as a service on management and compute/vis instances; leave ip as blank and set the port.

e.g. in management (same for compute/vis node):

Create new service in `/etc/systemd/system/socket-server.service` as below:
```
[Unit]
Description=socket-server

[Service]
User=ubuntu
Type=simple
ExecStart=/home/ubuntu/visualisation_scheduler/vs/bin/python3 /home/ubuntu/visualisation_scheduler/vscheduler/socket/mgmt-server.py
Restart=always

[Install]
WantedBy=multi-user.target
```
and enable/start it:
```
systemctl daemon-reload
systemctl enable socket-server.service
systemctl start socket-server.service
```

2. Locate `socket/*client.py` on management and compute/vis nodes in `/etc/profile.d/client.py` and set server's ip and port; For `mgmt-client.py` set ips of all destination nodes in a list where ip of management instance only is needed to be set in each `comp-client.py`. To run the script at each user login attempt in compute/vis node, add below line to `/etc/profile` on each node:
```
/usr/bin/python3 /etc/profile.d/client.py
```

3. Arrange admin access for management instance on each destination node by:
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
pip install --user virtualenv && PATH=$PATH:$HOME/.local/bin    # it's a good practice to have PATH in .bashrc
# OR
sudo apt install python3-virtualenv
# then:
virtualenv vs                           
# OR 
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
