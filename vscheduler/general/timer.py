# determines time brackets for searching bookings time slots
import sys, os, datetime
from time import gmtime, strftime
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials


class Brackets:

    now = datetime.datetime.utcnow()
    local_time = datetime.datetime.now()
    start_bracket = now - datetime.timedelta(hours=MyCredentials.booking_session)
    end_bracket = now + datetime.timedelta(hours=MyCredentials.booking_session)
    
    def what_time(now, local_time, start_bracket, end_bracket):
        time_records = Capture_log("general", __file__)
        logger = time_records.log_agent()
        
        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        print (
                f"""\nnow in system local timezome: {local_timezone} - {local_time}
                now in UTC: {now}, 
                start Bracket in UTC: {start_bracket}
                end Bracket in UTC: {end_bracket} 
                Difference: {end_bracket-start_bracket}\n"""
            ) if MyPrintCondition.fprint else 0
        logger.info (
                f"""\nnow in system local timezome: {local_timezone} - {local_time}
                now in UTC: {now}, 
                start Bracket in UTC: {start_bracket}
                end Bracket in UTC: {end_bracket} 
                Difference: {end_bracket-start_bracket}"""
            )