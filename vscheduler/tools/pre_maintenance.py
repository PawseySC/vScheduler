"""vmaintenance on/off: apply every maintenance change to vScheduler.

on  marks enabled nodes for maintenance, logs off non-exempt users, empties the
    general pools, renames the Guacamole portal group and stops mgmt_socket.
off starts mgmt_socket, runs the vhealth checks and, only if they all pass,
    returns maintained nodes to service, refills the general pools and restores
    the portal group name.
"""

import argparse
import io
import inspect
import sys
import time
from contextlib import redirect_stdout

from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.service import MGMT_SERVICE, control_service
from vscheduler.log.log import Capture_log
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.cluster.who import linux_sessions, who
from vscheduler.modules.guaca.pool_refresh import restore_empty_general_pool
from vscheduler.modules.guaca.portal import end_portal_maintenance, start_portal_maintenance
from vscheduler.modules.guaca.revert_user import revert_back_to_pool
from vscheduler.modules.reports.status import status_update
from vscheduler.tools.health import MGMT_PORT, run_checks

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


def logged_in_users(node):
    with redirect_stdout(io.StringIO()):
        if "include_exceptions" in inspect.signature(who).parameters:
            return who(node, include_exceptions=True)
        return who(node)


def logged_in_sessions(node):
    with redirect_stdout(io.StringIO()):
        return linux_sessions(node)


def print_session_table(sessions):
    columns = (
        ("USER", "user"),
        ("SESSION", "session_id"),
        ("KIND", "kind"),
        ("TYPE", "type"),
        ("REMOTE", "remote"),
        ("REMOTE HOST", "remote_host"),
        ("SERVICE", "service"),
        ("STATE", "state"),
    )
    rows = [
        [session.get(key, "") or "-" for _, key in columns]
        for session in sessions
    ]
    widths = [
        max([len(title)] + [len(row[index]) for row in rows])
        for index, (title, _) in enumerate(columns)
    ]
    print("  " + " | ".join(
        title.ljust(widths[index]) for index, (title, _) in enumerate(columns)
    ))
    print("  " + "-+-".join("-" * width for width in widths))
    for row in rows:
        print("  " + " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        ))


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
    is_windows = MyCredentials.windows_node_name in node
    sessions = None
    query_error = ""
    if not is_windows:
        try:
            sessions = logged_in_sessions(node)
        except Exception as error:
            users = None
            query_error = f": {error}"
        else:
            users = list(dict.fromkeys(
                session["user"] for session in sessions if session.get("user")
            ))
    else:
        users = logged_in_users(node)
    if users is None:
        message = f"Unable to query logged-in users on < {node} >{query_error}; skipping"
        print(f"{node}\n  {message}")
        logger.error(message)
        return
    if not users:
        message = "No users are logged in"
        print(f"{node}\n  {message}")
        logger.info(message)
        return

    print(node)
    if sessions is not None:
        if sessions:
            print_session_table(sessions)
        else:
            print("  No logind sessions")
    else:
        for user in users:
            print(f"  {user}")
    logger.info(f"Logged-in users: {', '.join(users)}")

    exceptions = {username.casefold() for username in MyCredentials.exception}
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
    exempt = [user for user in users if user.casefold() in exceptions]
    if exempt:
        message = f"Exempt users not logged off: {', '.join(exempt)}"
        print(f"  SKIP {message}")
        logger.info(message)
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


def maintenance_on(service=MGMT_SERVICE):
    nodes = configured_nodes()
    if not nodes:
        message = "No enabled nodes are configured; no maintenance preparation was performed"
        print(message)
        logger_win.warning(message)
        logger_unix.warning(message)
        return 0
    for index, node in enumerate(nodes):
        if index:
            print()
        prepare_node(node)

    status, message = start_portal_maintenance()
    print("\n{:<5} {}".format(status, message))
    log = logger_unix.error if status == "FAIL" else logger_unix.info
    log(message)
    portal_failed = status == "FAIL"

    # Stopped last so mgmt_socket still records the logoffs above.
    status, message = control_service("stop", service)
    print("{:<5} {}".format(status, message))
    log = logger_unix.error if status == "FAIL" else logger_unix.info
    log(message)
    return 1 if portal_failed or status == "FAIL" else 0


def is_general_node(node, prefix, enabled, node_range, booking_enabled, booking_range):
    if not node.startswith(prefix):
        return False
    node_number = int(node.removeprefix(prefix))
    return (
        enabled
        and node_number in range(node_range[0], node_range[1] + 1)
        and not (
            booking_enabled
            and node_number in range(booking_range[0], booking_range[1] + 1)
        )
    )


def report(status, message):
    print("{:<5} {}".format(status, message))
    log = logger_unix.error if status == "FAIL" else logger_unix.info
    log(message)


def restore_maintenance(current_status, portal_name):
    """Return maintained nodes to service, refill general pools, then restore the portal name."""
    maintenance_nodes = [
        node for node in configured_nodes() if current_status.get(node) == "maint"
    ]
    if not maintenance_nodes and portal_name != MyCredentials.guaca_maintenance_group_name:
        report("PASS", "Maintenance is already off")
        return True

    for node in maintenance_nodes:
        try:
            marked = status_update(node, "up")
            detail = ""
        except Exception as error:
            marked = False
            detail = ": {}".format(error)
        if not marked:
            report("FAIL", "Could not mark {} up{}".format(node, detail))
            return False

    general_candidates = {}
    for node in maintenance_nodes:
        if is_general_node(
            node,
            MyCredentials.windows_node_name,
            MyCredentials.windows_general,
            MyCredentials.windows_general_range,
            MyCredentials.windows_booking,
            MyCredentials.windows_booking_range,
        ):
            general_candidates.setdefault("windows", node)
        elif is_general_node(
            node,
            MyCredentials.linux_node_name,
            MyCredentials.linux_general,
            MyCredentials.linux_general_range,
            MyCredentials.linux_booking,
            MyCredentials.linux_booking_range,
        ):
            general_candidates.setdefault("linux", node)

    for operating_system, candidate_node in sorted(general_candidates.items()):
        try:
            restored = restore_empty_general_pool(operating_system, candidate_node)
            detail = ""
        except Exception as error:
            restored = False
            detail = ": {}".format(error)
        if not restored:
            report("FAIL", "Could not restore a Guacamole {} general pool connection{}".format(
                operating_system, detail))
            return False

    # Renamed last so users only see the normal portal once nodes and pools are back.
    status, message = end_portal_maintenance()
    report(status, message)
    if status == "FAIL":
        return False

    if maintenance_nodes:
        report("PASS", "Maintained nodes marked up: {}".format(", ".join(maintenance_nodes)))
    return True


def maintenance_off(host="127.0.0.1", port=MGMT_PORT, service=MGMT_SERVICE, timeout=3.0):
    status, message = control_service("start", service)
    report(status, message)
    print()
    failures, current_status, portal_name = run_checks(
        host, port, service, timeout, wait=message.endswith("started"),
    )
    print()
    if failures:
        report("FAIL", "{} health check(s) failed; maintenance left on. Fix the failures and "
               "run 'vmaintenance off' again".format(failures))
        return 1
    return 0 if restore_maintenance(current_status, portal_name) else 1


def main():
    parser = argparse.ArgumentParser(
        prog="vmaintenance",
        description="Turn vScheduler maintenance on or off. 'on' marks enabled nodes for "
        "maintenance, logs off non-exempt users, empties the general pools, renames the "
        "Guacamole portal group to guaca_maintenance_group_name, then prompts to stop the "
        "management service. 'off' prompts to start the management service, runs the vhealth "
        "checks and, only if all pass, returns maintained nodes to service, refills the "
        "general pools and renames the portal group back to guaca_portal_group_name.",
    )
    parser.add_argument("action", choices=("on", "off"), help="start or end maintenance")
    parser.add_argument("--host", default="127.0.0.1", help="expected local management listener address for 'off' checks (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=MGMT_PORT, help="management socket port for 'off' checks (default: %(default)s)")
    parser.add_argument("--service", default=MGMT_SERVICE, help="systemd management service name")
    parser.add_argument("--timeout", type=float, default=3.0, help="connection timeout in seconds for 'off' checks (default: %(default)s)")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    if args.action == "on":
        return maintenance_on(args.service)
    return maintenance_off(args.host, args.port, args.service, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
