# returns who's logged in each node
import re
from typing import Dict, List, Optional

from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.cluster.os_type import find_os

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")
logger_unix = booking_records.log_agent("linux")

LINUX_LIST_USERS = "loginctl list-users --no-legend | awk '{print $2}'"
LINUX_LIST_SESSIONS = "loginctl list-sessions --no-legend --no-pager"


def linux_sessions(node: str) -> List[Dict[str, str]]:
    """Return logind sessions with enough metadata to identify SSH and GUI logins.

    Raises an exception describing why the sessions could not be queried.
    """
    connection = None
    try:
        connection = MyNode.connect_node(node)
        if connection is None:
            raise ConnectionError(f"Could not connect to < {node} >")
        if find_os(node) != "Linux":
            raise RuntimeError(f"Cannot query Linux sessions on non-Linux node < {node} >")

        _, stdout, stderr = connection.exec_command(LINUX_LIST_SESSIONS)
        error = stderr.read() if stderr else b""
        if error:
            if isinstance(error, bytes):
                error = error.decode(errors="replace")
            raise RuntimeError(f"loginctl session query failed: {error.strip()}")

        sessions = []
        for line in stdout:
            fields = line.split()
            if not fields:
                continue
            # IDs are numeric, or e.g. "c1" for sessions without an audit session ID.
            if len(fields) < 3 or not re.fullmatch(r"[A-Za-z0-9_-]+", fields[0]):
                raise RuntimeError(f"Unexpected loginctl session row: {line.strip()}")

            session_id, username = fields[0], fields[2]
            _, detail_stdout, detail_stderr = connection.exec_command(
                f"loginctl show-session {session_id} "
                "-p Type -p Remote -p RemoteHost -p Service -p State"
            )
            detail_error = detail_stderr.read() if detail_stderr else b""
            if detail_error:
                if isinstance(detail_error, bytes):
                    detail_error = detail_error.decode(errors="replace")
                raise RuntimeError(
                    f"loginctl could not inspect session {session_id}: {detail_error.strip()}"
                )

            details = {}
            for detail in detail_stdout:
                key, separator, value = detail.rstrip("\n").partition("=")
                if separator:
                    details[key] = value

            session_type = details.get("Type", "")
            service = details.get("Service", "")
            remote = details.get("Remote", "")
            normalized_type = session_type.casefold()
            normalized_service = service.casefold()
            if "ssh" in normalized_service:
                kind = "SSH"
            elif normalized_type in {"x11", "wayland"}:
                kind = "GUI"
            elif normalized_type == "tty":
                kind = "TTY"
            else:
                kind = "Other"

            sessions.append({
                "session_id": session_id,
                "user": username,
                "kind": kind,
                "type": session_type,
                "remote": remote,
                "remote_host": details.get("RemoteHost", ""),
                "service": service,
                "state": details.get("State", ""),
            })
        return sessions
    finally:
        if connection is not None:
            connection.close()


def who(node: str, include_exceptions: bool = False) -> Optional[List[str]]:
    my_connection = None
    try:
        my_connection = MyNode.connect_node(node)
        if my_connection is None:
            raise ConnectionError(f"Could not connect to < {node} >")
        node_os = find_os(node)
        print (f"node_os=> {node_os}")

        if node_os == 'Windows':
            stdin , stdout, stderr = my_connection.exec_command("quser")
        elif node_os == 'Linux':
            # stdin , stdout, stderr = my_connection.exec_command("who")
            # utmp-based `who`/`users` can miss graphical sessions registered with logind.
            stdin , stdout, stderr = my_connection.exec_command(LINUX_LIST_USERS)
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.warning (f"no os found for < {node} >")
            return None

        users = []
        seen_users = set()
        exceptions = {name.casefold() for name in MyCredentials.exception}
        error = stderr.read() if stderr else b""
        if error:
            if node_os == "Linux":
                raise RuntimeError(f"loginctl user query failed: {error.decode(errors='replace').strip()}")
            print (f"Errors: {error}") if MyPrintCondition.fprint else 0
            logger_win.error (f"Errors: {error}") if MyCredentials.windows_node_name in node else logger_unix.error (f"Errors: {error}")
        for line in stdout:
            print (line.strip('\n')) if MyPrintCondition.fprint else 0
            logger_win.info (line.strip('\n')) if MyCredentials.windows_node_name in node else logger_unix.info (line.strip('\n'))
            fields = line.split()
            if not fields or line.strip().casefold().startswith("no user exists"):
                continue
            if fields[0] == ">":
                fields = fields[1:]
                if not fields:
                    continue
            username = fields[0].lstrip(">")
            normalized_username = username.casefold()
            if normalized_username == "username":
                continue
            if (
                (not include_exceptions and normalized_username in exceptions)
                or normalized_username in seen_users
            ):
                continue
            users.append(username)
            seen_users.add(normalized_username)
        return users

    except Exception as error:
        print (f"could not connect to < {node} > to query user: {error}") if MyPrintCondition.fprint else 0
        logger_win.error (f"could not connect to < {node} > to query user: {error}") if MyCredentials.windows_node_name in node else logger_unix.error (f"could not connect to < {node} > to query user: {error}")
        return None
    finally:
        if my_connection is not None:
            my_connection.close()