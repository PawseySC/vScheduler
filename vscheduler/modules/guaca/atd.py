import os, subprocess, time, sched
from subprocess import Popen, PIPE, CalledProcessError
from vscheduler.log.log import CaptureLog
from vscheduler.lib import config
from vscheduler.modules.reports.record_log_io import record_logout
from vscheduler.modules.guaca.revert_user import revert_back_to_pool

atd_records = CaptureLog("atd", __file__)
logger = atd_records.log_agent("guaca")

def post_log_off(user, node, table):
    """
    Returns user back to pool and records logout time in case of killing remote session as it forces remote session to be 
    closed without waiting for client's socket-based request to server to do so.
    """
    logger.info (f"post_log_ff start, user, node, table: {user}, {node}, {table}")
    revert_back_to_pool(user, node, config.partition['linux']['general']['pool'] if config.partition['linux']['node'] in node else config.partition['windows']['general']['pool'])
    record_logout(user, node, table, "general")
    logger.info ("post_log_ff end")
    
def at_daemon(user, node, table, walltime):
    """
    Manages sessions active time in general pool avoiding to stay longer than allowed wall-time
    """
    logger.info (f"at daemon start, user, node, table, walltime: {user}, {node}, {table}, {walltime}")
    # os.system(f'echo "vkill -u {user} -n {node} -v" | at now + {walltime} hour')
    command = f'echo "vkill -u {user} -n {node} -v" | /usr/bin/at now + {walltime} hour'
    subprocess.call(f"{command}", shell=True)
    # os.system(command)
    # result = os.popen(command).read()
    # logger_unix.info (f"Output from {command}:\n{result}")
    # scheduler = sched.scheduler(time.time, time.sleep)
    # specific_time = time.time() + walltime * 3600  # seconds from now
    # logger_unix.info (f"specific_time: {specific_time}")
    # scheduler.enterabs(specific_time, 1, post_log_off(user, node, table), ())
    # scheduler.run()
    logger.info ("at daemon end")
    # instead of above commands, can add "python /etc/profile.d/vis_client_logout.py" to log_off module for Linux client
    # instead of above commands, can add "python C:\ProgramData\Internal\vis_client_logout.py" to log_off module for Windows client
    
# post_log_off approach is less risky because triggering vis_client_logout.py at client remotely could be missed in case of busy resources on that node - above suggesstion ignored.