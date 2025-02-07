# calculates time brackets for bookings time slots searches
import datetime
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib import config

time_records = CaptureLog("timer", __file__)
logger = time_records.log_agent("general")

class Brackets:
    """
    Returns time arguments required for query from/to database(s)
    """
    # utc_now = datetime.datetime.utcnow()    # deprectaed
    utc_now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    local_time = datetime.datetime.now()
    start_bracket = utc_now - datetime.timedelta(hours = config.time['booking_session'])
    end_bracket = utc_now + datetime.timedelta(hours = config.time['booking_session'])
    
    def what_time(utc_now, local_time, start_bracket, end_bracket):
        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        print (
                f"""\nnow in system local timezome ({local_timezone}): {local_time}
                now in UTC: {utc_now}, 
                start Bracket in UTC: {start_bracket}
                end Bracket in UTC: {end_bracket} 
                Difference: {end_bracket-start_bracket}\n"""
            ) if PrintCondition.fprint else 0
        logger.info (
                f"""\nnow in system local timezome ({local_timezone}): {local_time}
                now in UTC: {utc_now}, 
                start Bracket in UTC: {start_bracket}
                end Bracket in UTC: {end_bracket} 
                Difference: {end_bracket-start_bracket}"""
            )