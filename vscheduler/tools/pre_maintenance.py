"""Mark configured nodes for maintenance and log off non-exempt desktop users."""

import io
import inspect
import sys
from contextlib import redirect_stdout

from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.log.log import Capture_log
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.cluster.who import who
from vscheduler.modules.guaca.empty_pool import empty_pool_connection
from vscheduler.modules.guaca.revert_user import revert_back_to_pool
from vscheduler.modules.reports.status import status_update

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


def general_pool_for_node(node):
    partitions = (
        (
            MyCredentials.windows_node_name,
            MyCredentials.windows_general,
            MyCredentials.windows_general_range,
            MyCredentials.windows_pool,
            MyCredentials.windows_booking,
            MyCredentials.windows_booking_range,
        ),
        (
            MyCredentials.linux_node_name,
            MyCredentials.linux_general,
            MyCredentials.linux_general_range,
            MyCredentials.linux_pool,
            MyCredentials.linux_booking,
            MyCredentials.linux_booking_range,
        ),
    )
    for prefix, enabled, node_range, pool, booking_enabled, booking_range in partitions:
        if not node.startswith(prefix):
            continue
        node_number = int(node.removeprefix(prefix))
        if (
            enabled
            and node_number in range(node_range[0], node_range[1] + 1)
            and not (
                booking_enabled
                and node_number in range(booking_range[0], booking_range[1] + 1)
            )
        ):
            return pool
    return None


def prepare_node(node):
    status_update(node, "maint")
    with redirect_stdout(io.StringIO()):
        if "include_exceptions" in inspect.signature(who).parameters:
            users = who(node, include_exceptions=True)
        else:
            users = who(node)
    logger = logger_win if MyCredentials.windows_node_name in node else logger_unix
    if users is None:
        message = f"Unable to query logged-in users on < {node} >; skipping"
        print(f"{node}\n  {message}")
        logger.error(message)
        return
    if not users:
        message = "No users are logged in"
        print(f"{node}\n  {message}")
        logger.info(message)
        return

    print(node)
    for user in users:
        print(f"  {user}")
    logger.info(f"Logged-in users: {', '.join(users)}")

    exceptions = {username.casefold() for username in MyCredentials.exception}
    is_windows = MyCredentials.windows_node_name in node
    prefix = MyCredentials.windows_node_name if is_windows else MyCredentials.linux_node_name
    node_number = int(node.removeprefix(prefix))
    booking_enabled = (
        MyCredentials.windows_booking if is_windows else MyCredentials.linux_booking
    )
    booking_range = (
        MyCredentials.windows_booking_range
        if is_windows
        else MyCredentials.linux_booking_range
    )
    is_booking_node = booking_enabled and node_number in range(
        booking_range[0], booking_range[1] + 1
    )
    pool = MyCredentials.windows_pool if is_windows else MyCredentials.linux_pool
    for user in users:
        if user.casefold() in exceptions:
            continue
        logoff(user, node)
        if is_booking_node:
            revert_back_to_pool(user, node, pool)


def main():
    if any(argument in ("-h", "--help") for argument in sys.argv[1:]):
        print("Usage: vmaintenance")
        print("Mark enabled nodes for maintenance and log off non-exempt users.")
        return

    nodes = configured_nodes()
    if not nodes:
        message = "No enabled nodes are configured; no maintenance preparation was performed"
        print(message)
        logger_win.warning(message)
        logger_unix.warning(message)
        return
    for index, node in enumerate(nodes):
        if index:
            print()
        prepare_node(node)

    for node in nodes:
        pool = general_pool_for_node(node)
        if pool:
            empty_pool_connection(node, "maintenance", pool)


if __name__ == "__main__":
    main()
