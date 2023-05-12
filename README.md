## Setup

By having [Guacamole](https://guacamole.apache.org/) and [booked](https://www.bookedscheduler.com/) installed, Python3 and pip3 are the only requirements to run the script (The script has been developed and tested based on Python 3.10.6.). All required packages will be automatically installed on management instance in step 1 below.

1. Setup virtual environemt on management instance

To have the script running environment clean and isolated, install all packages in a virtual environment avoiding confliction or version incompatibility issues with other tools/packages.

```

pip install --user virtualenv && PATH=$PATH:$HOME/.local/bin
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
- Click
- paramiko 3.0.0
- PyMySQL 1.0.2
- numpy 1.24.3
- tabulate
```

2. Setup admin access on each node
For session management on each node, create local admin:
```
sudo adduser admin
sudo usermod -aG sudo admin
```
Also, have public key of management instance populated over into `~/.ssh/authorized_keys` of admin profile on each node.

3. Set all parameters in `lib/config.py`

4. Enjoy the code! By having virtual environment activated, run `vmanage`, `vsync`, `vquota`, `valloc`, `vinfo`, `vreport`, `vcontrol` commands. For more info, run any of these commands with `-h`.