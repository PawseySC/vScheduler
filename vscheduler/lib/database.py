# establishes db connection to booked and guaca dbs
import sys
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.alert import mailFunction


module_records = Capture_log("database", __file__)
logger_module = module_records.log_agent()

try:
    import pymysql
except:
    print ('''
    You need pymysql module.
    https://pypi.org/project/PyMySQL/
    pip install PyMySQL\n''') if MyPrintCondition.fprint else 0
    logger_module.critical ('''
    \nYou need pymysql module.
    https://pypi.org/project/PyMySQL/
    pip install PyMySQL\n''')
    sys.exit(1)

class Database:    
    @staticmethod
    def connect_booked_db():
        databse_records = Capture_log("database", __file__)
        logger_booked = databse_records.log_agent()
        try:
            db_con = pymysql.connect(
                            host=MyCredentials.booked_host,
                            user=MyCredentials.booked_user, 
                            passwd=MyCredentials.booked_passwd,
                            db=MyCredentials.booked_db, 
                            port=MyCredentials.booked_port,
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            print (f"error connecting booked db\n{e}") if MyPrintCondition.fprint else 0
            mailFunction("db error", f"error connecting booked database\n{e}", "", "")
            logger_booked.critical (f"error connecting booked database\n{e}")
            quit()

    def connect_guaca_db():
        databse_records = Capture_log("database", __file__)
        logger_guaca = databse_records.log_agent()
        try:
            db_con = pymysql.connect(
                            host=MyCredentials.guaca_host,
                            user=MyCredentials.guaca_user, 
                            passwd=MyCredentials.guaca_passwd,
                            db=MyCredentials.guaca_db,
                            port=MyCredentials.guaca_port, 
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            print (f"error connecting guaca db\n{e}") if MyPrintCondition.fprint else 0
            mailFunction("db error", f"error connecting guaca database\n{e}", "", "")
            logger_guaca.critical (f"error connecting guaca database\n{e}")
            quit()

    def connect_report_db():
        databse_records = Capture_log("database", __file__)
        logger_guaca = databse_records.log_agent()
        try:
            db_con = pymysql.connect(
                            host=MyCredentials.report_host,
                            user=MyCredentials.report_user, 
                            passwd=MyCredentials.report_passwd,
                            db=MyCredentials.report_db,
                            port=MyCredentials.report_port, 
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            print (f"error connecting report db\n{e}") if MyPrintCondition.fprint else 0
            mailFunction("db error", f"error connecting report database\n{e}", "", "")
            logger_guaca.critical (f"error connecting report database\{e}")
            quit()