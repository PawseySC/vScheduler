# establishes db connection to booked and guaca dbs
import sys
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.alert import mailFunction
try:
    import pymysql
except:
    print ('''
    You need pymysql module.
    https://pypi.org/project/PyMySQL/
    pip install PyMySQL\n''')
    sys.exit(1)


class Database:    
    @staticmethod
    def connect_booked_db():
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
            print ("error connecting booked db")
            mailFunction("db error","error connecting booked database", "", "")
            quit()

    def connect_guaca_db():
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
            mailFunction("db error","error connecting guaca database", "", "")
            quit()