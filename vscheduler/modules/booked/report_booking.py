import os, sys
from pathlib import Path
from vscheduler.log.log import CaptureLog
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.modules.booked.host import host_by_name
from vscheduler.modules.booked.resource import resource_reservations
from vscheduler.modules.booked.reservation import user_reservations
from vscheduler.modules.booked.deleted import deleted_records
from vscheduler.modules.booked.user import user_details
from vscheduler.modules.booked.instances import reservation_instances
from datetime import timedelta

records = CaptureLog("booking", __file__)
logger_win = records.log_agent("windows")    # **** logger_unix needs to be added; win flag should be sent when calling the function ****


def booking_report_generator(username, hostname, start, end):
    
    directory = str(Path.home()) + "/visualisation_scheduler/vscheduler/reports" + str(hostname) + '\\' + str((MyBrackets.now.date() - timedelta(1)).year) + "/" + str((MyBrackets.now.date() - timedelta(1)).month) + '\\' + str((MyBrackets.now.date() - timedelta(1)).day)
    os.makedirs(directory) if not os.path.exists(directory) else 0
    my_html_report = open(directory + "/" + str(MyBrackets.now.date() - timedelta(1)) + ".html", "w")
    logger_win.info (f"{directory} was created")
    my_txt_report = open(directory + "/" + str(MyBrackets.now.date() - timedelta(1)) + ".txt","w")
    logger_win.info (f"{directory}/{my_txt_report} created")
    my_cumulative_report = open(directory + "/" + str(MyBrackets.now.date() - timedelta(1)) + ".dat","w")
    logger_win.info (f"{directory}/{my_cumulative_report} created")
    my_csv_report = open(directory + "/" + str(MyBrackets.now.date() - timedelta(1)) + ".csv","w")
    logger_win.info (f"{directory}/{my_csv_report} created")

    my_html_report.write ("<!DOCTYPE html>\n<html>\n<head>\n<script type='text/javascript' src='https://www.gstatic.com/charts/loader.js'></script>\n<style>\nbody{\nfont-family: monospace\n}\ntable {\nborder-collapse: collapse;\n}\ntable, td, th {\nborder: 1px solid grey;\n}\n</style>\n</head>\n<body>\n<img src='https://pawsey.org.au/wp-content/themes/project/img/pawsey-logo-blue.png' style='width: 150px'>\n<h3>" + str(today - timedelta(1)) + "\t/\t" + str(hostname) + "</h3>\n<table>\n<col>\n<colgroup span='2'></colgroup>\n<thead>\n<tr>\n<td colspan='5' style='background-color: #4caf4f66; text-align: center; font-weight: bold'>Booked</td>\n<td colspan='5' style='background-color: #af4c7166; text-align: center; font-weight: bold'>Actual</td>\n<td colspan='1' style='background-color: #4c8faf87; text-align: center; font-weight: bold'>Attempt</td>\n</tr>\n</thead>\n<thead style='background-color: #80808073'>\n<tr style='text-align: left;'>\n<th>Start Date</th>\n<th>Start Time</th>\n<th>End Date</th>\n<th>End Time</th>\n<th>Duration</th>\n<th>Start Date</th>\n<th>Start Time</th>\n<th>End Date</th>\n<th>End Time</th>\n<th>Duration</th>\n<th>Resolution</th>\n<th>First Name</th>\n<th>Last Name</th>\n<th>Pawsey Username</th>\n<th>email</th>\n<th>Reservation Date time</th>\n<th>Last Modified</th>\n<th>Status</th>\n</tr>\n</thead>\n<tbody>\n")

    resource = host_by_name(hostname)
    resource_reservation = resource_reservations(resource[0][0])
    reservation = user_reservations()
    reservation_series = deleted_records()
    users = user_details()
    reservation_instance = reservation_instances(MyBrackets.start_bracket, MyBrackets.end_bracket)

