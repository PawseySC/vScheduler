"""Read-only post-maintenance and post-restart health checks."""
import argparse
import shutil
import socket
import subprocess
import sys

from vscheduler.lib.config import Credentials as MyCredentials


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


def print_result(status, check, detail):
    print("{:<5} {}: {}".format(status, check, detail))


def check_systemd(service):
    systemctl = shutil.which("systemctl")
    if not systemctl:
        print_result("SKIP", "systemd service", "systemctl is not available")
        return True

    result = subprocess.run(
        [systemctl, "is-active", "--quiet", service],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        print_result("PASS", "systemd service", service + " is active")
        return True
    print_result("FAIL", "systemd service", service + " is not active")
    return False


def check_database(timeout):
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
        print_result("FAIL", "report database", str(error))
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
        print_result("FAIL", "report database schema", "missing or inaccessible tables: " + ", ".join(missing_tables))
        failures += 1
    else:
        print_result("PASS", "report database", "connection and required tables are available")

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
            print_result("WARN", "maintenance state", "still marked maint: " + ", ".join(maintenance_nodes))
        else:
            print_result("PASS", "maintenance state", "no nodes are currently marked maint")
    except Exception as error:
        print_result("FAIL", "maintenance state", str(error))
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

    print_result("INFO", "configured nodes", "checking {} enabled nodes".format(len(nodes)))
    for node, partition in nodes:
        fqdn = "{}.{}".format(node, MyCredentials.domain)
        state = current_status.get(node) if current_status is not None else None
        if state in ("maint", "down", "dev"):
            print_result("SKIP", node, "{} is marked {}; not probing SSH".format(partition, state))
            continue

        try:
            socket.getaddrinfo(fqdn, SSH_PORT, type=socket.SOCK_STREAM)
            check_tcp(fqdn, SSH_PORT, timeout)
            print_result("PASS", node, "{} resolves and SSH port {} accepts connections".format(partition, SSH_PORT))
        except (OSError, socket.gaierror) as error:
            print_result("FAIL", node, "{} SSH probe failed: {}".format(partition, error))
            failures += 1
            continue

        if MyCredentials.load_balance:
            try:
                with socket.create_connection((fqdn, VIS_PORT), timeout=timeout) as connection:
                    connection.settimeout(timeout)
                    connection.sendall(("health-check " + fqdn).encode("utf-8"))
                    response = connection.recv(1024).decode("utf-8", errors="replace")
                if response.startswith(node + ","):
                    print_result("PASS", node + " usage socket", "port {} returned usage data".format(VIS_PORT))
                else:
                    print_result("FAIL", node + " usage socket", "unexpected response: " + response[:120])
                    failures += 1
            except OSError as error:
                print_result("FAIL", node + " usage socket", str(error))
                failures += 1
    return failures


def main():
    parser = argparse.ArgumentParser(
        description="Run read-only checks after vScheduler maintenance or a system restart.",
        epilog="Also manually verify a sample vinfo query, a controlled allocation/login/logout, and the mgmt_socket service logs.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="expected local management listener address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=MGMT_PORT, help="management socket port (default: %(default)s)")
    parser.add_argument("--service", default="mgmt_socket.service", help="systemd management service name")
    parser.add_argument("--timeout", type=float, default=3.0, help="connection timeout in seconds (default: %(default)s)")
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    failures = 0
    listener = management_listener(args.host, args.port)
    if listener is True:
        print_result("PASS", "management socket", "{}:{} is listening".format(args.host, args.port))
    elif listener is False:
        print_result("FAIL", "management socket", "{}:{} is not listening".format(args.host, args.port))
        failures += 1
    else:
        print_result("SKIP", "management socket", "neither ss nor lsof is available for a safe listener check")

    if not check_systemd(args.service):
        failures += 1

    current_status, database_failures = check_database(args.timeout)
    failures += database_failures
    if current_status is None:
        pass
    else:
        failures += check_nodes(args.timeout, current_status)

    print("\n{} check(s) failed".format(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())