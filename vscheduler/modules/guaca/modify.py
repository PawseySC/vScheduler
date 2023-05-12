# removes user group record from guacamole deleting connection link from user's guacamole dashboard
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()


def modify(x,y):
    try:
        if x:
            reset = "DELETE FROM guacamole_user_group_member WHERE member_entity_id = '%s' AND user_group_id = '%s'" %(x, y)
        else:
            reset = "DELETE FROM guacamole_user_group_member WHERE user_group_id = '%s'" %(y)
        my_cursor.execute(reset)
        my_connection.commit()
        print(my_cursor.rowcount, "record(s) affected") if MyPrintCondition.fprint else 0
        if my_cursor.rowcount:
            print("session link was removed for member entiry id <", x,"> in user group id <", y,">") if MyPrintCondition.fprint and x else 0
            print("session link was removed for user group id <", y,">") if MyPrintCondition.fprint and not x else 0
    except:
        print ("error deleting recorde for member_entity_id <", x, "> and user_group_id <", y, ">") if MyPrintCondition.fprint else 0