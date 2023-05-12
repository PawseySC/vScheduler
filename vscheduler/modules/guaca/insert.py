# inserts new record as user group in guacamole makeing connection link in user's guacamole dashboard
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()


def insert(x,y):
    try:
        allocation = "INSERT INTO guacamole_user_group_member (member_entity_id, user_group_id) VALUES ('%s','%s')" %(x, y)  # WHERE member_entity_id
        my_cursor.execute(allocation)
        my_connection.commit()
        print(my_cursor.rowcount, "record(s) inserted") if MyPrintCondition.fprint else 0  
    except:
        print (f"error inserting record for user member entity id <", x, "> in group id <", y, ">") if MyPrintCondition.fprint else 0         