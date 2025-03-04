# establishes db connection to booked and guaca dbs
import sys, pymysql
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib.config import Config
from vscheduler.general.alert import mailFunction

database_records = CaptureLog("database", __file__)
logger = database_records.log_agent("lib")
config = Config()


class Database:
    """
    Establishes connection to database(s) from management server to query from/to
    """
    @staticmethod
    def connect_booked_db():
        try:
            if config.get("partition.windows.booking.status") or config.get("partition.linux.booking.status"):    # connect to booked db if necessary
                db_con = pymysql.connect(
                                host = config.get("database.booked.host"),
                                user = config.get("database.booked.user"),
                                passwd = config.get("database.booked.passwd"),
                                db = config.get("database.booked.db"),
                                port = config.get("database.booked.port"),
                                charset="utf8")
                return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting booked database\n{e}", "", "")
            logger.critical (f"error connecting booked database\n{e}")
            sys.exit (f"error connecting booked database\n{e}")

    def connect_guaca_db():
        try:
            db_con = pymysql.connect(                                           # connect to guaca db
                            host = config.get("database.guaca.host"),
                            user = config.get("database.guaca.user"),
                            passwd = config.get("database.guaca.passwd"),
                            db = config.get("database.guaca.db"),
                            port = config.get("database.guaca.port"),
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting guaca database\n{e}", "", "")
            logger.critical (f"error connecting guaca database\n{e}")
            sys.exit (f"error connecting guaca database\n{e}")

    def connect_report_db():
        try:
            db_con = pymysql.connect(                                           # connect to report db
                            host = config.get("database.report.host"),
                            user = config.get("database.report.user"),
                            passwd = config.get("database.report.passwd"),
                            db = config.get("database.report.db"),
                            port = config.get("database.report.port"),
                            charset="utf8")
            return db_con
        except pymysql.Error as e:
            mailFunction("db error", f"error connecting report database\n{e}", "", "")
            logger.critical (f"error connecting report database\n{e}")
            sys.exit (f"error connecting report database\n{e}")