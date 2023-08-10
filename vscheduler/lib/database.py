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
                            charset='utf8')
            return db_con
        except:
            print ("error connecting booked db") if MyPrintCondition.fprint else 0
            mailFunction("db error", "error connecting booked database", "", "")
            logger_booked.critical ("error connecting booked database")
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
                            charset='utf8')
            return db_con
        except:
            print ("error connecting guaca db") if MyPrintCondition.fprint else 0
            mailFunction("db error", "error connecting guaca database", "", "")
            logger_guaca.critical ("error connecting guaca database")
            quit()