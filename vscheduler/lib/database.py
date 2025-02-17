# establishes db connection to booked and guaca dbs
import sys, pymysql
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib import config
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
            if config.partition['windows']['booking']['status'] or config.partition['linux']['booking']['status']:    # connect to booked db if necessary
                db_con = pymysql.connect(
                                host = config.database['booked']['host'],
                                user = config.database['booked']['user'],
                                passwd = config.database['booked']['passwd'],
                                db = config.database['booked']['db'],
                                port = config.database['booked']['port'],
                                charset="utf8")
                return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting booked database\n{e}", "", "")
            logger.critical (f"error connecting booked database\n{e}")
            sys.exit (f"error connecting booked database\n{e}")

    def connect_guaca_db():
        try:
            db_con = pymysql.connect(                                           # connect to guaca db
                            host = config.database['guaca']['host'],
                            user = config.database['guaca']['user'],
                            passwd = config.database['guaca']['passwd'],
                            db = config.database['guaca']['db'],
                            port = config.database['guaca']['port'],
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting guaca database\n{e}", "", "")
            logger.critical (f"error connecting guaca database\n{e}")
            sys.exit (f"error connecting guaca database\n{e}")

    def connect_report_db():
        try:
            db_con = pymysql.connect(                                           # connect to report db
                            host = config.database['report']['host'],
                            user = config.database['report']['user'],
                            passwd = config.database['report']['passwd'],
                            db = config.database['report']['db'],
                            port = config.database['report']['port'],
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting report database\n{e}", "", "")
            logger.critical (f"error connecting report database\n{e}")
            sys.exit (f"error connecting report database\n{e}")