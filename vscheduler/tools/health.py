"""Post-maintenance and post-restart health checks."""
import argparse
import shutil
import socket
import subprocess
import sys
import time
from textwrap import fill

from tabulate import tabulate

from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.service import MGMT_SERVICE, control_service
from vscheduler.modules.reports.status import status_update
from vscheduler.modules.guaca.pool_refresh import restore_empty_general_pool
from vscheduler.modules.guaca.portal import end_portal_maintenance, portal_group_name


MGMT_PORT = 65001
VIS_PORT = 65002
SSH_PORT = 22


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


def check_nodes(timeout, current_status):
    failures = 0
    nodes = configured_nodes()
    if not nodes:
        print_result("WARN", "configured nodes", "no node partitions are enabled")
        return failures

    rows = []
    for node, partition in nodes:
        fqdn = "{}.{}".format(node, MyCredentials.domain)
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
            socket.getaddrinfo(fqdn, SSH_PORT, type=socket.SOCK_STREAM)
            check_tcp(fqdn, SSH_PORT, timeout)
            row["SSH"] = "PASS"
        except (OSError, socket.gaierror) as error:
            row["SSH"] = "FAIL"
            row["DETAILS"] = fill("SSH: " + str(error), width=55)
            failures += 1
            continue

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


def restore_maintenance_nodes(current_status):
    # configured_nodes lists a node once per active pool; overlapping pools would repeat it.
    maintenance_nodes = list(dict.fromkeys(
        node for node, _ in configured_nodes()
        if current_status.get(node) == "maint"
    ))
    portal_in_maintenance = (
        portal_group_name() == MyCredentials.guaca_maintenance_group_name
    )
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
        if not status_update(node, "up"):
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
        if not restore_empty_general_pool(operating_system, candidate_node):
            print_result(
                "FAIL",
                "{} general pool".format(operating_system),
                "could not restore a Guacamole pool connection",
            )
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
        description="Prompt to start the management service, then run checks after vScheduler maintenance or a system restart.",
        epilog="Also manually verify a sample vinfo query, a controlled allocation/login/logout, and the mgmt_socket service logs.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="expected local management listener address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=MGMT_PORT, help="management socket port (default: %(default)s)")
    parser.add_argument("--service", default=MGMT_SERVICE, help="systemd management service name")
    parser.add_argument("--timeout", type=float, default=3.0, help="connection timeout in seconds (default: %(default)s)")
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    failures = 0
    results = []
    start_status, start_message = control_service("start", args.service)
    started = start_message.endswith("started")
    if started or start_status == "FAIL" or start_message.endswith("declined"):
        print_result(start_status, "service start", start_message, results)

    listener = management_listener(args.host, args.port)
    if started:
        # A freshly started service may need a moment to bind its port.
        deadline = time.monotonic() + args.timeout
        while listener is False and time.monotonic() < deadline:
            time.sleep(0.5)
            listener = management_listener(args.host, args.port)
    if listener is True:
        print_result("PASS", "management socket", "{}:{} is listening".format(args.host, args.port), results)
    elif listener is False:
        print_result("FAIL", "management socket", "{}:{} is not listening".format(args.host, args.port), results)
        failures += 1
    else:
        print_result("SKIP", "management socket", "neither ss nor lsof is available for a safe listener check", results)

    if not check_systemd(args.service, results):
        failures += 1

    current_status, database_failures = check_database(args.timeout, results)
    failures += database_failures
    print(tabulate(results, headers=["CHECK", "RESULT", "DETAILS"], tablefmt="plain"))
    if current_status is None:
        pass
    else:
        failures += check_nodes(args.timeout, current_status)

    if failures:
        if current_status and any(
            status == "maint" for status in current_status.values()
        ):
            print_result(
                "WARN",
                "maintenance state",
                "left unchanged because health checks failed",
            )
    elif current_status is not None and not restore_maintenance_nodes(current_status):
        failures += 1
    print("\n{} check(s) failed".format(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())