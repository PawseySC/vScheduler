# manages sessions active time in general pool avoiding to stay longer than allowed wall-time
import os, time, sched
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.reports.record_log_io import record_logout
from vscheduler.modules.guaca.revert_user import revert_back_to_pool

atd_records = Capture_log("atd", __file__)
logger_unix = atd_records.log_agent("linux")

def post_log_off(user, node, table):
    logger_unix (f"post_log_ff start, user, node, table: {user, node, table}")
    revert_back_to_pool(user, node, MyCredentials.linux_pool if MyCredentials.linux_node_name in node else MyCredentials.windows_pool)
    record_logout(user, node, table, "general")
    logger_unix ("post_log_ff end")
    
def at_daemon(user, node, table, walltime):
    logger_unix (f"at daemon start, user, node, table, walltime: {user, node, table, walltime}")
    os.system(f'echo "vkill -u {user} -n {node} -v" | at now + {walltime} hour')
    scheduler = sched.scheduler(time.time, time.sleep)
    specific_time = time.time() + walltime * 3600  # seconds from now
    scheduler.enterabs(specific_time, 1, post_log_off(user, node, table), ())
    scheduler.run()
    logger_unix ("at daemon end")
    # instead of above commands, can add "python /etc/profile.d/vis_client_logout.py" to log_off module for Linux client
    # instead of above commands, can add "python C:\ProgramData\Internal\vis_client_logout.py" to log_off module for Windows client
    
# post_log_off approach is less risky because triggering vis_client_logout.py at client remotely could be missed in case of busy resources on that node - above suggesstion ignored.