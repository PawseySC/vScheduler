# establishes db connection to booked and guaca dbs
import sys
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib.config import Credentials
from vscheduler.general.alert import mailFunction


database_records = Capture_log("database", __file__)
logger = database_records.log_agent("lib")

try:
    import pymysql
except:
    print ('''
    You need pymysql module.
    https://pypi.org/project/PyMySQL/
    pip install PyMySQL\n''') if PrintCondition.fprint else 0
    logger.critical ('''
    \nYou need pymysql module.
    https://pypi.org/project/PyMySQL/
    pip install PyMySQL\n''')
    sys.exit(1)

class Database:    
    @staticmethod
    def connect_booked_db():
        try:
            if Credentials.windows_booking or Credentials.linux_booking:    # connect to booked db if necessary
                db_con = pymysql.connect(
                                host=Credentials.booked_host,
                                user=Credentials.booked_user, 
                                passwd=Credentials.booked_passwd,
                                db=Credentials.booked_db, 
                                port=Credentials.booked_port,
                                charset="utf8")
                return db_con
        except pymysql.Error as e:
            print (f"error connecting booked database\n{e}") if PrintCondition.fprint else 0
            mailFunction("db error", f"error connecting booked database\n{e}", "", "")
            logger.critical (f"error connecting booked database\n{e}")
            quit()

    def connect_guaca_db():
        try:
            db_con = pymysql.connect(                                           # connect to guaca db
                            host=Credentials.guaca_host,
                            user=Credentials.guaca_user, 
                            passwd=Credentials.guaca_passwd,
                            db=Credentials.guaca_db,
                            port=Credentials.guaca_port, 
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            print (f"error connecting guaca database\n{e}") if PrintCondition.fprint else 0
            mailFunction("db error", f"error connecting guaca database\n{e}", "", "")
            logger.critical (f"error connecting guaca database\n{e}")
            quit()

    def connect_report_db():
        try:
            db_con = pymysql.connect(                                           # connect to report db
                            host=Credentials.report_host,
                            user=Credentials.report_user, 
                            passwd=Credentials.report_passwd,
                            db=Credentials.report_db,
                            port=Credentials.report_port, 
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            print (f"error connecting report database\n{e}") if PrintCondition.fprint else 0
            mailFunction("db error", f"error connecting report database\n{e}", "", "")
            logger.critical (f"error connecting report database\n{e}")
            quit()