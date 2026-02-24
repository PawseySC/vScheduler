Vscheduler Release Notes
---
<!-- [v1.0](https://github.com/PawseySC/visualisation_scheduler/files/15033083/vscheduler1.0.zip) -->
[v1.0](https://github.com/PawseySC/visualisation_scheduler/releases/tag/v1.0)
---
Following features are included in current release:
- Logging
- email notification for db disconnections and socket communication failure
- In-built modules:
    * vsync → booked-guacamole sync
    * vmanage → windows machines management
    * vreport → report module
    * vkill → end a session
    * vquota → report on quota for specific group or node
    * valloc → allocates a node to user
- read config from dedicated config file
- load balance
- socket communication between management and visualisation nodes
- CLI wrapper
- session management through ssh 
- record login/out events in local db on management instance
- client side socket server to send usage back to management instance for load balance
- no re-allocation of same node to same user after log out
- multithread modules