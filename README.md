<img src="vs.png" alt="vScheduler" width="400">

# **vScheduler** 
## **Pawsey Supercomputing Centre**

> [!NOTE] 
> Following procedure tested on Ubuntu 22.04 with MySQL 8.0.36 and Python 3.10.6.
> By having [Guacamole](https://guacamole.apache.org/) and [booked](https://www.bookedscheduler.com/) installed, Python3 and pip3 are the only requirements to run the script. All required packages will be automatically installed on Management Instance in step A.2 below.

## Terminologies

* **Management Instance** - The instance hosting vis scheduler
* **Client** - Remote visualisation nodes
* **Socket Server** - Socket server running on Management Instance or Clients
* **Socket Client** - Socket clients running on Management Instance or Clients

## A. Management Instance Setup

1. Clone the vis scheduler repo

2. Setup virtual environemt on Management Instance

    To have the script running environment clean and isolated, install all packages in a virtual environment avoiding confliction or version incompatibility issues with other tools/packages.

    ```
    sudo apt install python3-pip            # install pip
    sudo apt install python3-venv
    python3 -m venv .venv
    #sudo apt install python3-virtualenv     # install virtual environment
    #virtualenv .venv                         # setup virtual environment
    source .venv/bin/activate                # activate virtual environment
    (.venv) $ pip install -e .               # run in setup.py directory to install all required packages inside virtual environment
    deactivate                              # to exit from virtual environment
    ```
    Above will install follwing packages along with their dependencies in python virtual environment:
    ```
    - Click 8.1.3
    - paramiko 3.0.0
    - PyMySQL 1.0.2
    - numpy 1.24.3
    - tabulate 0.9.0
    - rich 13.3.5
    - jinja2 3.1.2
    - plotly 5.16.1
    - kaleido 0.2.1
    - calmap==0.0.11
    - calplot==0.1.7.5
    ```
    _Optional:_ It's a good practice to source virtual environment in `.bashrc`
    > **Tip**: To activate virtual environment automatically when navigating to the local repo directory, add following to `.bashrc`:
    ```
    function cd() {
    builtin cd "$@"

    if [[ -z "$VIRTUAL_ENV" ]] ; then
        ## If env folder is found then activate the vitualenv
        if [[ -d ./.env ]] ; then
            source ./.env/bin/activate
        fi
    else
        ## check the current folder belong to earlier VIRTUAL_ENV folder
        # if yes then do nothing
        # else deactivate
        parentdir="$(dirname "$VIRTUAL_ENV")"
        if [[ "$PWD"/ != "$parentdir"/* ]] ; then
            deactivate
        fi
    fi
    }
    ```

3. Setup MySQL database for report:
    ```
    sudo apt install mysql-server
    sudo mysql
        create database report;
        use report;
        CREATE TABLE windows (
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            node VARCHAR(255),
            user VARCHAR(255),
            pool VARCHAR(255),
            start DATETIME,
            end DATETIME,
            PRIMARY KEY (id)
            );
        CREATE TABLE linux (
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            node VARCHAR(255),
            user VARCHAR(255),
            pool VARCHAR(255),
            start DATETIME,
            end DATETIME,
            PRIMARY KEY (id)
            );
        CREATE TABLE status (
            id MEDIUMINT NOT NULL AUTO_INCREMENT,
            node VARCHAR(255),
            status VARCHAR(255),
            pool VARCHAR(255),
            start DATETIME,
            end DATETIME,
            PRIMARY KEY (id)
            );
        CREATE TABLE exception (
            id MEDIUMINT NOT NULL AUTO_INCREMENT, 
            user VARCHAR(255),
            start DATETIME,
            end DATETIME,
            wall_time int,
            PRIMARY KEY (id)
            );
        use mysql;
        create user 'reporter'@'%' IDENTIFIED WITH mysql_native_password BY 'PASSWORD';
        grant all privileges on report.* to 'reporter'@'%';
        flush privileges;
        quit
    ```
    _Optional:_ To access db remotely, add `bind-address            = 0.0.0.0` to `/etc/mysql/mysql.conf.d/mysqld.cnf` and restart MySQl server:
    ```
    sudo systemctl restart mysql
    ```

4. Set all parameters in `vscheduler/lib/config.py`

5. Create new service in `/etc/systemd/system/mgmt_socket.service` as below:
    ```
    [Unit]
    Description=mgmt_socket

    [Service]
    User=ubuntu
    Type=simple
    ExecStart=/home/ubuntu/visualisation_scheduler/.env/bin/python3 /home/ubuntu/visualisation_scheduler/vscheduler/socket/mgmt_server.py
    Environment="PATH=/home/ubuntu/visualisation_scheduler/.env/bin"
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


## B. Client Setup

1. Copy `vscheduler/socket/vis*.py` files to `/etc/profile.d/` on each vis node and set Management Instance ip and port

2. To run login/out scripts at users' login/out events in Clients, add below:

    **login**:
    add below line to BOF: `/etc/profile`
    ```
    /usr/bin/python3 /etc/profile.d/vis_client_login.py
    ```

    **logout**:
    add below line to EOF `/etc/bash.bash_logout`:
    ```
    /usr/bin/python3 /etc/profile.d/vis_client_logout.py
    ```

    > **NOTE**: above works only for ssh; adjust releavant files for other protocols (RDP, VNC) depending on the installed desktop manager on Clients.

3. Arrange admin access for Management Instance on each destination Client node:
    ```
    sudo adduser admin
    sudo usermod -aG sudo admin
    ```
    and, popoulate public key of Management Instance over into `~/.ssh/authorized_keys` of admin profile on each Client for passwordless communication.

4. Create new service in `/etc/systemd/system/vis_socket.service` on Clients as below to run `vscheduler/socket/vis_server.py` as a service: (_IMPORTANT:_ leave ip as blank and pick different port than socket server(s) on Management Instance)
    > This socket server is explicitely used to pass usage data to Management Instance load balancer.

    ```
    [Unit]
    Description=vis_socket

    [Service]
    User=admin
    Type=simple
    ExecStart=/usr/bin/python3 /etc/profile.d/vis_server.py
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

## C. RUN

Enjoy the code! By having virtual environment activated, you can run `vmanage`, `vsync`, `vquota`, `valloc`, `vinfo`, `vset`, `vreport`, `vcontrol`, `vkill` commands. For more info, run any of these commands with `-h`.
> **NOTE**: Separate log files will be created in `vscheduler/log` with the same name set in `vscheduler/lib/config/py` for `windows_node_name` and `linux_node_name`.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.