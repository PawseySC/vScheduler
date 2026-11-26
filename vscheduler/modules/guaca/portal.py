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
        autocommit=False,
        connect_timeout=10,
    )


def portal_group_name():
    """Return the current portal group name, or None if the group does not exist.

    Database errors are raised so callers can report them.
    """
    with _connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            f"SELECT connection_group_name FROM {GROUP_TABLE} WHERE connection_group_id = %s",
            (MyCredentials.guaca_portal_group_id,),
        )
        row = cursor.fetchone()
    return row[0] if row else None


def lock_portal_group(cursor, group_id):
    """Serialize maintenance transitions with general-pool permission writes."""
    cursor.execute(
        f"SELECT connection_group_name FROM {GROUP_TABLE} WHERE connection_group_id = %s FOR UPDATE",
        (group_id,),
    )
    return cursor.fetchone()


def set_portal_group_name(name, *, empty_pools=()):
    """Rename the configured portal group to `name`; return (status, message)."""
    group_id = MyCredentials.guaca_portal_group_id
    try:
        with _connect() as connection, connection.cursor() as cursor:
            row = lock_portal_group(cursor, group_id)
            if row is None:
                return "FAIL", f"Guacamole connection group {group_id} was not found"
            for pool in empty_pools:
                cursor.execute(
                    "SELECT entity_id FROM guacamole_entity WHERE name = %s AND type = 'USER_GROUP'",
                    (pool,),
                )
                entity = cursor.fetchone()
                if entity is None:
                    return "FAIL", f"Guacamole general pool '{pool}' was not found"
                cursor.execute(
                    "DELETE FROM guacamole_connection_permission WHERE entity_id = %s",
                    (entity[0],),
                )
            if row[0] != name:
                cursor.execute(
                    f"UPDATE {GROUP_TABLE} SET connection_group_name = %s WHERE connection_group_id = %s",
                    (name, group_id),
                )
            connection.commit()
    except pymysql.MySQLError as error:
        return "FAIL", f"could not update Guacamole connection group {group_id} and its maintenance pools: {error}"
    if row[0] == name:
        message = f"Guacamole connection group {group_id} is already named '{name}'"
    else:
        message = f"Guacamole connection group renamed from '{row[0]}' to '{name}'"
    if empty_pools:
        message += f"; emptied general pool(s): {', '.join(empty_pools)}"
    return "PASS", message


def start_portal_maintenance():
    pools = tuple(dict.fromkeys(
        pool for enabled, pool in (
            (MyCredentials.windows_general, MyCredentials.windows_pool),
            (MyCredentials.linux_general, MyCredentials.linux_pool),
        ) if enabled
    ))
    return set_portal_group_name(MyCredentials.guaca_maintenance_group_name, empty_pools=pools)


def end_portal_maintenance():
    return set_portal_group_name(MyCredentials.guaca_portal_group_name)
