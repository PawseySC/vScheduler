# determines time brackets for searching bookings time slots
import sys, os, datetime
from time import gmtime, strftime
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials


class Brackets:

    now = datetime.datetime.utcnow()
    start_bracket = now - datetime.timedelta(hours=MyCredentials.booking_session)
    end_bracket = now + datetime.timedelta(hours=MyCredentials.booking_session)
    
    def what_time(now, start_bracket, end_bracket):
        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        print (
                f"now in system local timezome,", local_timezone, ":", datetime.datetime.now(), 
                "\nnow in UTC: ", now, 
                "\nstart Bracket in UTC: ", start_bracket, 
                "\nend Bracket in UTC: ", end_bracket, 
                "\nDifference: ", end_bracket-start_bracket, "\n"
            ) if MyPrintCondition.fprint else 0