"""Renames the Guacamole portal connection group while maintenance is in progress."""
import pymysql

from vscheduler.lib.config import Credentials as MyCredentials

GROUP_TABLE = "guacamole_connection_group"


def _connect():
    # Connect directly rather than via Database.connect_guaca_db, which quits the
    # process on failure; callers need a reportable error instead.
    return pymysql.connect(
        host=MyCredentials.guaca_host,
        user=MyCredentials.guaca_user,
        password=MyCredentials.guaca_passwd,
        database=MyCredentials.guaca_db,
        port=MyCredentials.guaca_port,
        charset="utf8",
        connect_timeout=10,
    )


def portal_group_name():
    """Return the current portal group name, or None if it cannot be read."""
    try:
        with _connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"SELECT connection_group_name FROM {GROUP_TABLE} WHERE connection_group_id = %s",
                (MyCredentials.guaca_portal_group_id,),
            )
            row = cursor.fetchone()
    except pymysql.MySQLError:
        return None
    return row[0] if row else None


def set_portal_group_name(name):
    """Rename the configured portal group to `name`; return (status, message)."""
    group_id = MyCredentials.guaca_portal_group_id
    try:
        with _connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                f"SELECT connection_group_name FROM {GROUP_TABLE} WHERE connection_group_id = %s",
                (group_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return "FAIL", f"Guacamole connection group {group_id} was not found"
            if row[0] == name:
                return "PASS", f"Guacamole connection group {group_id} is already named '{name}'"
            cursor.execute(
                f"UPDATE {GROUP_TABLE} SET connection_group_name = %s WHERE connection_group_id = %s",
                (name, group_id),
            )
            connection.commit()
    except pymysql.MySQLError as error:
        return "FAIL", f"could not rename Guacamole connection group {group_id} to '{name}': {error}"
    return "PASS", f"Guacamole connection group renamed from '{row[0]}' to '{name}'"


def start_portal_maintenance():
    return set_portal_group_name(MyCredentials.guaca_maintenance_group_name)


def end_portal_maintenance():
    return set_portal_group_name(MyCredentials.guaca_portal_group_name)
