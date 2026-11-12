"""Mark configured nodes for maintenance and log off non-exempt desktop users."""

import io
import inspect
import sys
import time
from contextlib import redirect_stdout

from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.service import MGMT_SERVICE, control_service
from vscheduler.log.log import Capture_log
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.cluster.who import who
from vscheduler.modules.guaca.empty_pool import empty_pool_connection
from vscheduler.modules.guaca.portal import start_portal_maintenance
from vscheduler.modules.guaca.revert_user import revert_back_to_pool
from vscheduler.modules.reports.status import status_update

records = Capture_log("maintenance", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")

# Session teardown (utmp/quser update) can lag behind pkill/logoff.
VERIFY_ATTEMPTS = 3
VERIFY_DELAY = 2


def configured_nodes():
    """Return every node within the range of an active (enabled) booking or general pool."""
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
        if not enabled:
            continue
        for number in range(node_range[0], node_range[1] + 1):
            node = f"{prefix}{number:02d}" if number <= 9 else f"{prefix}{number}"
            # A node shared with an inactive pool's range is still an active pool member.
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


def logged_in_users(node):
    with redirect_stdout(io.StringIO()):
        if "include_exceptions" in inspect.signature(who).parameters:
            return who(node, include_exceptions=True)
        return who(node)


def remaining_sessions(node, users, attempts=VERIFY_ATTEMPTS, delay=VERIFY_DELAY):
    """Return users from `users` still logged in on `node`, or None if it can't be queried."""
    targets = {user.casefold() for user in users}
    remaining = None
    for attempt in range(attempts):
        if attempt:
            time.sleep(delay)
        current = logged_in_users(node)
        if current is None:
            continue
        remaining = [user for user in current if user.casefold() in targets]
        if not remaining:
            return []
    return remaining


def prepare_node(node):
    logger = logger_win if MyCredentials.windows_node_name in node else logger_unix
    try:
        marked = status_update(node, "maint")
        detail = ""
    except Exception as error:
        # status_update also refreshes the Guacamole pool; a failure there must not stop the logoffs.
        marked = False
        detail = f": {error!r}"
    if not marked:
        message = f"Could not set < {node} > status to maint{detail}; logging off users anyway"
        print(f"{node}\n  {message}")
        logger.error(message)
    users = logged_in_users(node)
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
    targets = [user for user in users if user.casefold() not in exceptions]
    for user in targets:
        try:
            logoff(user, node)
            if is_booking_node:
                revert_back_to_pool(user, node, pool)
        except Exception as error:
            message = f"Error logging off < {user} > on < {node} >: {error!r}"
            print(f"  {message}")
            logger.error(message)
    if not targets:
        return

    remaining = remaining_sessions(node, targets)
    if remaining is None:
        message = "Unable to verify that sessions were killed"
        print(f"  WARN {message}")
        logger.warning(message)
    elif remaining:
        message = f"Sessions still active after logoff: {', '.join(remaining)}"
        print(f"  FAIL {message}")
        logger.error(message)
    else:
        message = f"Sessions killed: {', '.join(targets)}"
        print(f"  PASS {message}")
        logger.info(message)


def main():
    if any(argument in ("-h", "--help") for argument in sys.argv[1:]):
        print("Usage: vmaintenance")
        print("Mark enabled nodes for maintenance, log off non-exempt users,")
        print("empty general pools, rename the Guacamole portal group to")
        print("'{}', then prompt to stop the {} service.".format(
            MyCredentials.guaca_maintenance_group_name, MGMT_SERVICE))
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
            try:
                empty_pool_connection(node, "maintenance", pool)
            except Exception as error:
                message = f"Could not remove < {node} > from < {pool} > pool: {error!r}"
                print(f"\nFAIL  {message}")
                logger_unix.error(message)

    status, message = start_portal_maintenance()
    print("\n{:<5} {}".format(status, message))
    log = logger_unix.error if status == "FAIL" else logger_unix.info
    log(message)

    # Stopped last so mgmt_socket still records the logoffs above.
    status, message = control_service("stop")
    print("{:<5} {}".format(status, message))
    log = logger_unix.error if status == "FAIL" else logger_unix.info
    log(message)


if __name__ == "__main__":
    main()
