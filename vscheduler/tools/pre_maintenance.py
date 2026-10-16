"""Log out desktop users before maintenance is applied to configured nodes."""

import sys

from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.log.log import Capture_log
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.cluster.who import who

records = Capture_log("maintenance", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")


def configured_nodes():
    nodes = []
    partitions = (
        (
            MyCredentials.windows_node_name,
            MyCredentials.windows_booking,
            MyCredentials.windows_booking_range,
        ),
        (
            MyCredentials.windows_node_name,
            MyCredentials.windows_general,
            MyCredentials.windows_general_range,
        ),
        (
            MyCredentials.linux_node_name,
            MyCredentials.linux_booking,
            MyCredentials.linux_booking_range,
        ),
        (
            MyCredentials.linux_node_name,
            MyCredentials.linux_general,
            MyCredentials.linux_general_range,
        ),
    )
    for prefix, enabled, node_range in partitions:
        if enabled:
            for number in range(node_range[0], node_range[1] + 1):
                node = f"{prefix}{number:02d}" if number <= 9 else f"{prefix}{number}"
                if node not in nodes:
                    nodes.append(node)
    return nodes


def prepare_node(node):
    users = who(node, include_exceptions=True)
    logger = logger_win if MyCredentials.windows_node_name in node else logger_unix
    if users is None:
        message = f"Unable to query logged-in users on < {node} >; skipping"
        print(message) if MyPrintCondition.fprint else 0
        logger.error(message)
        return
    if not users:
        message = f"No users are logged in to < {node} >"
        print(message) if MyPrintCondition.fprint else 0
        logger.info(message)
        return

    message = f"Logged-in users on < {node} >: {', '.join(users)}"
    print(message)
    logger.info(message)
    exceptions = {username.casefold() for username in MyCredentials.exception}
    for user in users:
        if user.casefold() in exceptions:
            continue
        logoff(user, node)


def main():
    if any(argument in ("-h", "--help") for argument in sys.argv[1:]):
        print("Usage: vmaintenance")
        print("Log off non-exempt users from enabled nodes before maintenance.")
        return

    nodes = configured_nodes()
    if not nodes:
        message = "No enabled nodes are configured; no maintenance preparation was performed"
        print(message)
        logger_win.warning(message)
        logger_unix.warning(message)
        return
    for node in nodes:
        prepare_node(node)


if __name__ == "__main__":
    main()
