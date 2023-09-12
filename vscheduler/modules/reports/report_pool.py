import os, sys
from pathlib import Path
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.modules.booked.host import host_by_name
from vscheduler.modules.booked.resource import resource_reservations
from vscheduler.modules.booked.reservation import user_reservations
from vscheduler.modules.booked.deleted import deleted_records
from vscheduler.modules.booked.user import user_details
from vscheduler.modules.booked.instances import reservation_instances
from vscheduler.general.alert import mailFunction
from vscheduler.general.alert2 import email_with_embeded_image
import datetime
from datetime import timedelta
from jinja2 import Template
import plotly.graph_objects as go
from plotly.subplots import make_subplots

my_connection = MyDatabase.connect_report_db()

records = Capture_log("pool", __file__)
logger = records.log_agent()


def pool_report_generator(hostname, username, start, end):
    counter = 0
    # directory = str(Path.home()) + "/visualisation_scheduler/vscheduler/reports" #+ str(hostname) + '\\' + str((MyBrackets.now.date() - timedelta(1)).year) + "/" + str((MyBrackets.now.date() - timedelta(1)).month) + '\\' + str((MyBrackets.now.date() - timedelta(1)).day)
    # os.makedirs(directory) if not os.path.exists(directory) else 0
    # html_report = open(directory + "/" + str(MyBrackets.now.date() - timedelta(1)) + ".html", "w")
    # html_report.write ("<!DOCTYPE html>\n<html>\n<head>\n<script type='text/javascript' src='https://www.gstatic.com/charts/loader.js'></script>\n<style>\nbody{\nfont-family: monospace\n}\ntable {\nborder-collapse: collapse;\n}\ntable, td, th {\nborder: 1px solid grey;\n}\n</style>\n</head>\n<body>\n<img src='https://pawsey.org.au/wp-content/themes/project/img/pawsey-logo-beige.png' style='width: 150px'>\n<h3>" + str(MyBrackets.now.date() - timedelta(1)) + "\t/\t" + str(hostname) + "</h3>\n<table>\n<col>\n<colgroup span='2'></colgroup>\n<thead>\n<tr>\n<td colspan='5' style='background-color: #4caf4f66; text-align: center; font-weight: bold'>Node</td>\n<td colspan='5' style='background-color: #af4c7166; text-align: center; font-weight: bold'>General Partition</td>\n<td colspan='1' style='background-color: #4c8faf87; text-align: center; font-weight: bold'>Identification</td>\n</tr>\n</thead>\n<thead style='background-color: #80808073'>\n<tr style='text-align: left;'>\n<th>Start Date-Time</th>\n<th>End Date-Time</th>\n<th>Duration</th>\n<th>First Name</th>\n<th>Last Name</th>\n<th>Username</th>\n<th>email</th>\n</tr>\n</thead>\n<tbody>\n")

    
    # try:
    # statistics
    sentence = []
    query = ""
    accumulation = 0

    query = " WHERE " if hostname or username or start or end else 0
    if query:
        if hostname:
            query = query + f"node = '{hostname}'"
            if username:
                query = query + f" AND user = '{username}'"
                if start:
                    query = query + f" AND start >= '{start}'"
                    if end:
                        query = query + f" AND end <= '{end}'"          
        else:
            if username:
                query = query + f"user = '{username}'"
                if start:
                    query = query + f" AND start >= '{start}'"
                    if end:
                        query = query + f" AND end <= '{end}'"
            else:
                if start:
                    query = query + f"start >= '{start}'"
                    if end:
                        query = query + f" AND end <= '{end}'"
                else:
                    if end:
                        query = query + f"end <= '{end}'"
                        
    # print (query)
    actual_usage_report = f"SELECT * FROM {MyCredentials.report_linux_table}" + query
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(actual_usage_report)
        actual_usage_report_results = my_cursor.fetchall()
    count=0
    for row_usage in actual_usage_report_results:
        count += 1
        node = row_usage[1]
        user = row_usage[2]
        pool = row_usage[3]
        date_from = row_usage[4]
        date_to = row_usage[5]
        duration = date_to - date_from
        if pool == 'general':
            if count==1:
                accumulation = duration
            else:
                accumulation += duration
            sentence.insert(len(sentence), [node, date_from, date_to, duration, user, '', '', ''])
        
        # counter = counter + 1
        # if counter%2 == 0:
        #     color = "#001fff0d"
        # else:
        #     color = "white"
        # html_report.write("<tr style='background-color:" + str(color) +"'>\n<td>" + str(node) + "</td>\n<td>" + str(date_from) + "</td>\n<td>" + str(date_to) + "</td>\n<td>" + str(duration) + "</td>\n<td>" + "" + "</td>\n<td>" + "" + "</td>\n<td>" + name + "</td>\n<td>" + "" + "</td>\n<td>")

    print(tabulate(sentence, headers=['node', 'start', 'end', 'duration', 'user', 'email', 'first name', 'last name'])) if MyPrintCondition.fprint else 0
    logger.info ("\n" + tabulate(sentence, headers=['node', 'start', 'end', 'duration', 'user', 'email', 'first name', 'last name']))
    print (f"in total: {accumulation}")


    # visuals:
    labels = []
    val = []
    for item in sentence:
        if item[4] in labels:
            index = labels.index(item[4])
            val[index] += item[3] / accumulation * 100
        else:
            labels.append (item[4]) # usernames
            val.append (item[3] / accumulation * 100)
    
    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels=labels, values=val, name=hostname), 1, 1)
    
    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
        title_text="Usage Report for " + hostname,
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=hostname, x=0.18, y=0.5, font_size=20, showarrow=False)])
    
    directory = str(Path.home()) + "/visualisation_scheduler/vscheduler/modules/reports"
    os.makedirs(directory) if not os.path.exists(directory) else 0
    
    fig.write_image(f"{directory}/fig1.png")
    fig.show()



    html="""\
    <html>
    <head>
    </head>
    <body>
    <img src='https://pawsey.org.au/wp-content/themes/project/img/pawsey-logo-beige.png' style='width: 150px'>
    <table style="border-collapse:collapse;border-spacing:0;">
        <thead>
            <tr>
                <td colspan='1' style='background-color: #4caf4f66; text-align: center; font-weight: bold;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;'>Node</td>
                <td colspan='3' style='background-color: #af4c7166; text-align: center; font-weight: bold;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;'>General Partition</td>
                <td colspan='4' style='background-color: #4c8faf87; text-align: center; font-weight: bold;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;'>Identification</td>
            </tr>
        </thead>
        <thead style='background-color: #80808073'>
            <tr style='text-align: left;'>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">Hostname</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">Start</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">End</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">Duration</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">Username</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">Email</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">FirstN</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">LastN</td>              
            </tr>
        </thead>
        {% for title in titles %}
            <tr>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[0]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[1]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[2]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[3]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[4]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[5]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[6]}}</td>
                <td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;">{{title[7]}}</td>
            </tr>
        {% endfor %}
    </table>
    <img src="cid:{image_cid}"></body>
    </html>"""
    
    my_templ = Template(html)
    mailFunction (f"Report for {hostname} {username} {str(start)} {str(end)}", my_templ.render(titles=sentence), directory, ['fig1.png'])
    email_with_embeded_image(my_templ.render(titles=sentence))
    # mailFunction ('subject', my_templ.render (titles=tabulate(sentence, tablefmt="html")), '', '')
    # return  actual_usage_report_results, accumulation

    # import smtplib

    # from email.mime.multipart import MIMEMultipart
    # from email.mime.text import MIMEText
    # from email.mime.image import MIMEImage
    # from_addr= 'noreply@pawsey.org.au'
    # to_addr= 'ali.zamani@pawsey.org.au'
    # msg = MIMEMultipart('alternative')
    # msg['Subject'] = "subject"
    # msg['From'] = from_addr
    # msg['To'] = to_addr

    # text = MIMEText('<h3>hi</h3><img src="cid:image1">', 'html')
    # msg.attach(text)

    # image = MIMEImage(open(f'{directory}/fig1.png', 'rb').read())

    # # Define the image's ID as referenced in the HTML body above
    # image.add_header('Content-ID', '<image1>')
    # msg.attach(image)

    # s = smtplib.SMTP('mail-server.pawsey.org.au')
    # s.sendmail(from_addr, to_addr, msg.as_string())
    # s.quit()


  


    # except:
    #     print (f"error: records for < {hostname} >, < {username} >, < {start} >, < {end} > was not found in report database") if MyPrintCondition.fprint else 0
    #     logger.error(f"records for < {hostname} >, < {username} >, < {start} >, < {end} > was not found in report database")