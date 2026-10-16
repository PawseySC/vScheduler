# returns who's logged in each node
from typing import List, Optional

from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.ssh import Node as MyNode
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.cluster.os_type import find_os

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")
logger_unix = booking_records.log_agent("linux")


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
            stdin , stdout, stderr = my_connection.exec_command("who")
        else:
            print (f"no os found for < {node} >") if MyPrintCondition.fprint else 0
            logger_win.warning (f"no os found for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.warning (f"no os found for < {node} >")
            return None

        users = []
        seen_users = set()
        exceptions = {name.casefold() for name in MyCredentials.exception}
        if stderr:
            error = stderr.read()
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