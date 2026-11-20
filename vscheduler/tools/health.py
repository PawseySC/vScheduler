"""Post-maintenance and post-restart health checks."""
import argparse
import importlib
import shutil
import socket
import subprocess
import sys
import time
from textwrap import fill

from tabulate import tabulate

from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.service import MGMT_SERVICE, control_service
from vscheduler.modules.guaca.portal import end_portal_maintenance, portal_group_name


MGMT_PORT = 65001
VIS_PORT = 65002
SSH_PORT = 22


def load_helper(module, name):
    """Import a database-backed helper on first use.

    These modules connect to the report/Guacamole databases at import time and
    exit if that fails, so importing them up front would stop vhealth before it
    could report the failing database.
    """
    try:
        return getattr(importlib.import_module(module), name)
    except SystemExit as error:
        raise RuntimeError(str(error) or "could not load " + module) from None


def status_update(node, mode):
    return load_helper("vscheduler.modules.reports.status", "status_update")(node, mode)


def restore_empty_general_pool(operating_system, candidate_node):
    return load_helper(
        "vscheduler.modules.guaca.pool_refresh", "restore_empty_general_pool",
    )(operating_system, candidate_node)


def check_tcp(host, port, timeout):
    with socket.create_connection((host, port), timeout=timeout):
        return True


def management_listener(host, port):
    ss = shutil.which("ss")
    if ss:
        result = subprocess.run(
            [ss, "-ltn"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, check=False,
        )
        if result.returncode == 0:
            try:
                expected_addresses = {
                    item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
                }
            except socket.gaierror:
                expected_addresses = {host}
            for line in result.stdout.splitlines()[1:]:
                fields = line.split()
                if len(fields) < 4 or fields[0] != "LISTEN":
                    continue
                address, listening_port = fields[3].rsplit(":", 1)
                address = address.strip("[]")
                if listening_port == str(port) and (
                    address in ("*", "0.0.0.0", "::") or address in expected_addresses
                ):
                    return True
            return False

    lsof = shutil.which("lsof")
    if lsof:
        result = subprocess.run(
            [lsof, "-nP", "-iTCP:{}".format(port), "-sTCP:LISTEN"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        return result.returncode == 0
    return None


def configured_nodes():
    nodes = []
    partitions = (
        ("Windows booking", MyCredentials.windows_booking, MyCredentials.windows_node_name, MyCredentials.windows_booking_range),
        ("Windows general", MyCredentials.windows_general, MyCredentials.windows_node_name, MyCredentials.windows_general_range),
        ("Linux booking", MyCredentials.linux_booking, MyCredentials.linux_node_name, MyCredentials.linux_booking_range),
        ("Linux general", MyCredentials.linux_general, MyCredentials.linux_node_name, MyCredentials.linux_general_range),
    )
    for partition, enabled, prefix, node_range in partitions:
        if enabled:
            start, end = node_range
            nodes.extend(
                (prefix + str(index).zfill(2), partition)
                for index in range(start, end + 1)
            )
    return nodes


def print_result(status, check, detail, results=None):
    if results is not None:
        results.append((check, status, fill(detail, width=65)))
    else:
        print("{:<5} {}: {}".format(status, check, detail))


def describe(error):
    return str(error) or type(error).__name__


def guarded(item, results, fallback, check, *args):
    """Run one check; an unexpected error becomes a FAIL row for that item instead of stopping vhealth."""
    try:
        return check(*args)
    except Exception as error:
        print_result("FAIL", item, describe(error), results)
        return fallback


CHECK_ERROR = object()


def check_service(host, port, service, timeout, results=None, wait=False):
    """Report the management socket and systemd service; return the number of failures."""
    failures = 0
    listener = guarded("management socket", results, CHECK_ERROR, management_listener, host, port)
    if wait:
        # A freshly started service may need a moment to bind its port.
        deadline = time.monotonic() + timeout
        while listener is False and time.monotonic() < deadline:
            time.sleep(0.5)
            listener = guarded("management socket", results, CHECK_ERROR, management_listener, host, port)
    if listener is True:
        print_result("PASS", "management socket", "{}:{} is listening".format(host, port), results)
    elif listener is False:
        print_result("FAIL", "management socket", "{}:{} is not listening".format(host, port), results)
        failures += 1
    elif listener is None:
        print_result("SKIP", "management socket", "neither ss nor lsof is available for a safe listener check", results)
    else:
        failures += 1

    if not guarded("systemd service", results, False, check_systemd, service, results):
        failures += 1
    return failures


def check_portal(results=None):
    """Report the Guacamole portal group name; return (name or None, failures)."""
    missing = [
        setting for setting in (
            "guaca_portal_group_id",
            "guaca_portal_group_name",
            "guaca_maintenance_group_name",
        )
        if not hasattr(MyCredentials, setting)
    ]
    if missing:
        print_result("FAIL", "Guacamole portal", "add missing Credentials settings in vscheduler/lib/config.py: {}".format(
            ", ".join(missing),
        ), results)
        return None, 1

    group_id = MyCredentials.guaca_portal_group_id
    try:
        name = portal_group_name()
    except Exception as error:
        print_result("FAIL", "Guacamole portal", "could not read connection group {}: {}".format(group_id, describe(error)), results)
        return None, 1
    if name is None:
        print_result("FAIL", "Guacamole portal", "connection group {} was not found".format(group_id), results)
        return None, 1
    if name == MyCredentials.guaca_maintenance_group_name:
        print_result("WARN", "Guacamole portal", "named '{}' (maintenance)".format(name), results)
    elif name == MyCredentials.guaca_portal_group_name:
        print_result("PASS", "Guacamole portal", "named '{}'".format(name), results)
    else:
        print_result("WARN", "Guacamole portal", "named '{}'; expected '{}'".format(
            name, MyCredentials.guaca_portal_group_name), results)
    return name, 0


def check_systemd(service, results=None):
    systemctl = shutil.which("systemctl")
    if not systemctl:
        print_result("SKIP", "systemd service", "systemctl is not available", results)
        return True

    result = subprocess.run(
        [systemctl, "is-active", "--quiet", service],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        print_result("PASS", "systemd service", service + " is active", results)
        return True
    print_result("FAIL", "systemd service", service + " is not active", results)
    return False


def check_database(timeout, results=None):
    try:
        import pymysql

        connection = pymysql.connect(
            host=MyCredentials.report_host,
            user=MyCredentials.report_user,
            password=MyCredentials.report_passwd,
            database=MyCredentials.report_db,
            port=MyCredentials.report_port,
            connect_timeout=timeout,
            read_timeout=timeout,
            write_timeout=timeout,
        )
    except Exception as error:
        print_result("FAIL", "report database", str(error), results)
        return None, 1

    required_tables = {
        MyCredentials.report_status_table,
        MyCredentials.report_exception_table,
    }
    if MyCredentials.windows_booking or MyCredentials.windows_general:
        required_tables.add(MyCredentials.report_windows_table)
    if MyCredentials.linux_booking or MyCredentials.linux_general:
        required_tables.add(MyCredentials.report_linux_table)

    missing_tables = []
    for table in sorted(required_tables):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM `{}` LIMIT 0".format(table))
        except Exception:
            missing_tables.append(table)

    failures = 0
    if missing_tables:
        print_result("FAIL", "report database schema", "missing or inaccessible tables: " + ", ".join(missing_tables), results)
        failures += 1
    else:
        print_result("PASS", "report database", "connection and required tables are available", results)

    current_status = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT node, status FROM `{}` WHERE start = end".format(
                    MyCredentials.report_status_table
                )
            )
            for node, status in cursor.fetchall():
                current_status[node] = str(status).lower()
        maintenance_nodes = sorted(
            node for node, status in current_status.items() if status == "maint"
        )
        if maintenance_nodes:
            print_result("WARN", "maintenance state", "still marked maint: " + ", ".join(maintenance_nodes), results)
        else:
            print_result("PASS", "maintenance state", "no nodes are currently marked maint", results)
    except Exception as error:
        print_result("FAIL", "maintenance state", str(error), results)
        current_status = None
        failures += 1

    connection.close()
    return current_status, failures


def probe_node(row, node, partition, timeout):
    """Probe one node's SSH, RDP and (with load balancing) usage service, filling in its row."""
    failures = 0
    fqdn = "{}.{}".format(node, MyCredentials.domain)
    try:
        socket.getaddrinfo(fqdn, SSH_PORT, type=socket.SOCK_STREAM)
        check_tcp(fqdn, SSH_PORT, timeout)
        row["SSH"] = "PASS"
    except (OSError, socket.gaierror) as error:
        row["SSH"] = "FAIL"
        row["DETAILS"] = fill("SSH: " + str(error), width=55)
        failures += 1
        return failures

    if partition.startswith(("Linux", "Windows")):
        server = "xrdp" if partition.startswith("Linux") else "Microsoft RDP"
        try:
            check_tcp(fqdn, MyCredentials.rdp_port, timeout)
            row["RDP"] = "PASS"
        except OSError as error:
            row["RDP"] = "FAIL"
            row["DETAILS"] = fill(server + ": " + str(error), width=55)
            failures += 1

    if MyCredentials.load_balance:
        try:
            with socket.create_connection((fqdn, VIS_PORT), timeout=timeout) as connection:
                connection.settimeout(timeout)
                connection.sendall(("health-check " + fqdn).encode("utf-8"))
                response = connection.recv(1024).decode("utf-8", errors="replace")
            if response.startswith(node + ","):
                row["USAGE"] = "PASS"
            else:
                row["USAGE"] = "FAIL"
                row["DETAILS"] += ("\n" if row["DETAILS"] else "") + fill(
                    "Usage: unexpected response: " + response[:120], width=55,
                )
                failures += 1
        except OSError as error:
            row["USAGE"] = "FAIL"
            row["DETAILS"] += ("\n" if row["DETAILS"] else "") + fill(
                "Usage: " + str(error), width=55,
            )
            failures += 1
    return failures


def check_nodes(timeout, current_status):
    failures = 0
    nodes = configured_nodes()
    if not nodes:
        print_result("WARN", "configured nodes", "no node partitions are enabled")
        return failures

    rows = []
    for node, partition in nodes:
        state = current_status.get(node) if current_status is not None else None
        row = {
            "NODE": node,
            "PARTITION": partition,
            "STAT": state or "-",
            "SSH": "-",
            "RDP": "-",
        }
        if MyCredentials.load_balance:
            row["USAGE"] = "-"
        row["DETAILS"] = ""
        rows.append(row)
        if state in ("down", "dev"):
            row["SSH"] = row["RDP"] = "SKIP"
            if MyCredentials.load_balance:
                row["USAGE"] = "SKIP"
            continue

        try:
            failures += probe_node(row, node, partition, timeout)
        except Exception as error:
            # Unexpected errors are reported on this node's row; the remaining nodes are still checked.
            row["DETAILS"] += ("\n" if row["DETAILS"] else "") + fill("Error: " + describe(error), width=55)
            failures += 1
    print("\nNodes (SSH: {}; RDP: {} = Linux xrdp / Windows Microsoft RDP{})".format(
        SSH_PORT, MyCredentials.rdp_port,
        "; usage: {}".format(VIS_PORT) if MyCredentials.load_balance else "",
    ))
    print(tabulate(rows, headers="keys", tablefmt="plain"))
    return failures


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


def restore_maintenance_nodes(current_status, portal_name=None):
    # configured_nodes lists a node once per active pool; overlapping pools would repeat it.
    maintenance_nodes = list(dict.fromkeys(
        node for node, _ in configured_nodes()
        if current_status.get(node) == "maint"
    ))
    if portal_name is None:
        portal_name = portal_group_name()
    portal_in_maintenance = portal_name == MyCredentials.guaca_maintenance_group_name
    if not maintenance_nodes and not portal_in_maintenance:
        return True

    try:
        answer = input(
            "All health checks passed. Bring maintained nodes to status 'up' "
            "and rename '{}' back to '{}'? [y/N]: ".format(
                MyCredentials.guaca_maintenance_group_name,
                MyCredentials.guaca_portal_group_name,
            )
        ).strip().casefold()
    except EOFError:
        print_result("WARN", "maintenance state", "no confirmation received; left unchanged")
        return True
    if answer not in ("y", "yes"):
        print_result("INFO", "maintenance state", "left unchanged")
        return True

    for node in maintenance_nodes:
        try:
            marked = status_update(node, "up")
        except Exception as error:
            print_result("FAIL", "maintenance state", "could not mark {} up: {}".format(node, error))
            return False
        if not marked:
            print_result("FAIL", "maintenance state", "could not mark {} up".format(node))
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
            detail = "could not restore a Guacamole pool connection"
        except Exception as error:
            restored = False
            detail = "could not restore a Guacamole pool connection: {}".format(error)
        if not restored:
            print_result("FAIL", "{} general pool".format(operating_system), detail)
            return False

    # Renamed last so users only see the normal portal once nodes and pools are back.
    status, message = end_portal_maintenance()
    print_result(status, "Guacamole portal", message)
    if status == "FAIL":
        return False

    if maintenance_nodes:
        print_result("PASS", "maintenance state", "maintained nodes marked up")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Check vScheduler after maintenance or a system restart: report every check first, "
        "then prompt to start the management service and to end maintenance.",
        epilog="Also manually verify a sample vinfo query, a controlled allocation/login/logout, and the mgmt_socket service logs.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="expected local management listener address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=MGMT_PORT, help="management socket port (default: %(default)s)")
    parser.add_argument("--service", default=MGMT_SERVICE, help="systemd management service name")
    parser.add_argument("--timeout", type=float, default=3.0, help="connection timeout in seconds (default: %(default)s)")
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    # 1. Report: every check runs and shows its own result or error; nothing is changed yet.
    results = []
    service_failures = check_service(args.host, args.port, args.service, args.timeout, results)
    current_status, database_failures = guarded(
        "report database", results, (None, 1), check_database, args.timeout, results,
    )
    portal_name, portal_failures = check_portal(results)
    print(tabulate(results, headers=["CHECK", "RESULT", "DETAILS"], tablefmt="plain"))
    node_failures = guarded(
        "node checks", None, 1, check_nodes, args.timeout, current_status or {},
    )
    failures = service_failures + database_failures + portal_failures + node_failures

    # 2. Changes: prompted only after all results are shown.
    print()
    try:
        start_status, start_message = control_service("start", args.service)
    except Exception as error:
        start_status, start_message = "FAIL", "could not start {}: {}".format(args.service, describe(error))
    started = start_message.endswith("started")
    if started or start_status == "FAIL" or start_message.endswith("declined"):
        print_result(start_status, "service start", start_message)
    if started:
        new_service_failures = check_service(args.host, args.port, args.service, args.timeout, wait=True)
        failures += new_service_failures - service_failures

    if failures:
        in_maintenance = (
            portal_name is not None and portal_name == MyCredentials.guaca_maintenance_group_name
        ) or any(status == "maint" for status in (current_status or {}).values())
        if in_maintenance:
            print_result("WARN", "maintenance state", "left unchanged because health checks failed")
    elif not guarded(
        "maintenance state", None, False, restore_maintenance_nodes, current_status, portal_name,
    ):
        failures += 1
    print("\n{} check(s) failed".format(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())