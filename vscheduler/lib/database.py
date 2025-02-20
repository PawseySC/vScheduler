# establishes db connection to booked and guaca dbs
import sys, pymysql
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib.config import Config
from vscheduler.general.alert import mailFunction

database_records = CaptureLog("database", __file__)
logger = database_records.log_agent("lib")


class Database:
    """
    Establishes connection to database(s) from management server to query from/to
    """
    @staticmethod
    def connect_booked_db():
        try:
            if Config.config['partition']['windows']['booking']['status'] or Config.config['partition']['linux']['booking']['status']:    # connect to booked db if necessary
                db_con = pymysql.connect(
                                host = Config.config['database']['booked']['host'],
                                user = Config.config['database']['booked']['user'],
                                passwd = Config.config['database']['booked']['passwd'],
                                db = Config.config['database']['booked']['db'],
                                port = Config.config['database']['booked']['port'],
                                charset="utf8")
                return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting booked database\n{e}", "", "")
            logger.critical (f"error connecting booked database\n{e}")
            sys.exit (f"error connecting booked database\n{e}")

    def connect_guaca_db():
        try:
            db_con = pymysql.connect(                                           # connect to guaca db
                            host = Config.config['database']['guaca']['host'],
                            user = Config.config['database']['guaca']['user'],
                            passwd = Config.config['database']['guaca']['passwd'],
                            db = Config.config['database']['guaca']['db'],
                            port = Config.config['database']['guaca']['port'],
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting guaca database\n{e}", "", "")
            logger.critical (f"error connecting guaca database\n{e}")
            sys.exit (f"error connecting guaca database\n{e}")

    def connect_report_db():
        try:
            db_con = pymysql.connect(                                           # connect to report db
                            host = Config.config['database']['report']['host'],
                            user = Config.config['database']['report']['user'],
                            passwd = Config.config['database']['report']['passwd'],
                            db = Config.config['database']['report']['db'],
                            port = Config.config['database']['report']['port'],
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting report database\n{e}", "", "")
            logger.critical (f"error connecting report database\n{e}")
            sys.exit (f"error connecting report database\n{e}")