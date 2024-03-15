# vinfo script
import multiprocessing, click, time
from vscheduler.log.log import Capture_log
from tabulate import tabulate
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.reports.information import print_info

records = Capture_log("info", __file__)
logger_win = records.log_agent("info")


def main():
    print_info()

if __name__ == '__main__':
    main()