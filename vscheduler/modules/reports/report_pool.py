import os, warnings
warnings.filterwarnings('ignore')
import pandas as pd
import calmap, matplotlib
# from plotly_calplot import calplot
from pathlib import Path
from tabulate import tabulate
# from pretty_html_table import build_table
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.initiate import Initiation as initiate
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.alert import mailFunction
from vscheduler.general.alert2 import email_with_embeded_image
from jinja2 import Template
import datetime

my_connection = MyDatabase.connect_report_db()

records = Capture_log("pool", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")


def pool_report_generator(hostname, username, start, end):
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
    actual_usage_report_results = pd.read_sql(actual_usage_report, my_connection)
    actual_usage_report_results["email"] = ""
    actual_usage_report_results["first name"] = ""
    actual_usage_report_results["last name"] = ""
    actual_usage_report_results["institute"] = ""

    columns_title = ["id", "node", "start", "end", "duration", "pool", "user", "email", "first name", "last name"]
    
    actual_usage_report_results3 = actual_usage_report_results
    actual_usage_report_results3 = actual_usage_report_results3.reindex(columns=columns_title)
    actual_usage_report_results3["duration"] = actual_usage_report_results3["end"] - actual_usage_report_results3["start"]
    actual_usage_report_results3_list = actual_usage_report_results3.values.tolist()

    actual_usage_report_results = actual_usage_report_results.drop(columns=["id"])
    columns_title = ["node", "start", "end", "duration", "pool", "user", "email", "first name", "last name", "institute"]
    actual_usage_report_results = actual_usage_report_results.reindex(columns=columns_title)
    print (actual_usage_report_results.values.tolist())
    actual_usage_report_results["duration"] = actual_usage_report_results["end"] - actual_usage_report_results["start"]
    actual_usage_report_results2 = actual_usage_report_results
    actual_usage_report_results_list = actual_usage_report_results.values.tolist()
    actual_usage_report_results = actual_usage_report_results.set_index("node")
    actual_usage_report_results_html = actual_usage_report_results.to_html(classes="table table-stripped", border="collpase")
    print (actual_usage_report_results_list)
    print (tabulate(actual_usage_report_results, headers='keys', tablefmt='psql'))
    print ("sum: ", actual_usage_report_results['duration'].sum())
    logger_win.info ("\n" + tabulate(actual_usage_report_results, headers='keys', tablefmt='psql')) if MyCredentials.windows_node_name in hostname else logger_unix.info ("\n" + tabulate(actual_usage_report_results, headers='keys', tablefmt='psql'))
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
            sentence.insert(len(sentence), [node, date_from, date_to, duration, user, '', '', '', ''])
        

    print(tabulate(sentence, headers=['node', 'start', 'end', 'duration', 'user', 'email', 'first name', 'last name', 'institute'], tablefmt='psql')) if MyPrintCondition.fprint else 0
    # logger.info ("\n" + tabulate(sentence, headers=['node', 'start', 'end', 'duration', 'user', 'email', 'first name', 'last name'], tablefmt='psql'))
    print (f"in total: {accumulation}")


    # visuals: 
    directory = str(Path.home()) + "/visualisation_scheduler/vscheduler/modules/reports"
    os.makedirs(directory) if not os.path.exists(directory) else 0
    if username and hostname:
        print ("-u -n")
        actual_usage_report_results2["duration"] = actual_usage_report_results2['duration'].dt.total_seconds()/3600
        dummy_df = pd.DataFrame(actual_usage_report_results2)
        # dummy_df.set_index("start").reset_index()
        # print ("dummy_df:\n", dummy_df["start"].values, dummy_df["duration"].values)
        # fig = calplot(
        #         dummy_df,
        #         x="start",
        #         y="duration"
        # )
        # fig.show()
        # fig.write_image(f"{directory}/fig1.png", scale=1)
        import calplot
        import matplotlib.pyplot as plt
        d= actual_usage_report_results2["duration"]
        print ("d",d, type(d))
        s= dummy_df["start"]
        print ("s", s, type(s))
        
        f= pd.concat([d, s], axis=1)
        print ("f", f, type(f))
        g=f["duration"].squeeze()
        print ("g", g, type(g))
        values = pd.Series(dummy_df.duration.values, index = dummy_df.start)
        # values = dummy_df["duration"].squeeze()
        print ("values:\n", values)

        # series_name_age = df[['Name', 'Age']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
        # values2 = dummy_df[["start", "duration"]].apply(lambda x: ', '.join(x.astype(str)), axis=1)
        # print ("values2:\n", values2)
        # values3 = pd.Series(values2[1], index=values2[0])
        # print ("values3", values3)
        calplot.calplot(values, how="sum",
                        suptitle = '',
                        suptitle_kws = {'x': 0.5, 'y': 1.0})
        plt.show()
        plt.savefig(f"{directory}/fig1.png")
            # df = px.data.tips()
            # df = pd.DataFrame(actual_usage_report_results2)
            # fig = px.histogram(df, x="duration")
            # fig.show()
        # actual_usage_report_results2["duration"] = actual_usage_report_results2['duration'].dt.total_seconds()/3600
        # df_heatmaps = pd.DataFrame(actual_usage_report_results2)
        # df_heatmaps.set_index('start', inplace=True)
        # import matplotlib.pyplot as plt
        # from mpl_toolkits.axes_grid1 import make_axes_locatable
        # yyyy = 2023
        # fig = plt.figure(figsize=(20,4))
        # ax = fig.add_subplot(111)
        # cax = calmap.yearplot(df_heatmaps['duration'], year=yyyy)                                                                                                                                                                                           
        # plt.xlabel("Trades grouped by day", fontsize=12)
        # plt.ylabel(yyyy, fontsize=58, color='#f5f5f5', weight='bold')
        # fig.suptitle('Number of trades per day heatmap', fontsize=16)
        # divider = make_axes_locatable(cax)
        # lcax = divider.append_axes("right", size="2%", pad=0.5)
        # fig.colorbar(cax.get_children()[1], cax=lcax)
        
        # # all_days = pd.date_range('1/15/2022', periods=700, freq='D')
        # # events = pd.Series(df_heatmaps["duration"])
        # # fig_heatmaps = calmap.yearplot(events, year=2023)

        # # fig_heatmaps = px.pie(df_pie, values='duration', names='user', title='Usage by Vis Users')
        # fig.show()
        # # print ("timedelta" , actual_usage_report_results2['duration'].dt.total_seconds()/3600)
        # # actual_usage_report_results2["duration"] = actual_usage_report_results2['duration'].dt.total_seconds()/3600
        # # actual_usage_report_results2 = actual_usage_report_results2.sort_values(by='node')
        # # df = pd.DataFrame(actual_usage_report_results2)
        # # fig = px.bar(df, x="node", y="duration", text_auto='.4s', color="node", title="Usage by Vis Nodes")
        # # fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        # # fig.update_layout(xaxis_title='Vis Node', yaxis_title='Duration (hrs)', yaxis=dict(tickformat="duration",), bargap = 0.8,)

    elif not username and not hostname:
        df_pie = pd.DataFrame(actual_usage_report_results2)
        fig_pie = px.pie(df_pie, values='duration', names='user', title='Usage by Vis Users')
        fig_pie.show()
        fig_pie.write_image(f"{directory}/fig1.png", scale=1)
        print ("timedelta" , actual_usage_report_results2['duration'].dt.total_seconds()/3600)
        actual_usage_report_results2["duration"] = actual_usage_report_results2['duration'].dt.total_seconds()/3600
        actual_usage_report_results2 = actual_usage_report_results2.sort_values(by='node')
        df = pd.DataFrame(actual_usage_report_results2)
        fig_bar = px.bar(df, x="node", y="duration", text_auto='.4s', color="node", title="Usage by Vis Nodes")
        fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        fig_bar.update_layout(xaxis_title='Vis Node', yaxis_title='Duration (hrs)', yaxis=dict(tickformat="duration",), bargap = 0.8,)
        fig_bar.show()
        fig_bar.write_image(f"{directory}/fig2.png", scale=1)
        # fig_histogram = px.histogram(df, x="node")
        # fig_histogram.update_layout(bargap=0)
        # fig_histogram.show()

    else:
        labels = []
        val = []
        for item in sentence:
            if hostname and not username:
                if item[4] in labels:
                    index = labels.index(item[4])
                    val[index] += item[3] / accumulation * 100
                else:
                    labels.append (item[4]) # usernames
                    val.append (item[3] / accumulation * 100)
            if username and not hostname:
                if item[4] in labels:
                    index = labels.index(item[0])
                    val[index] += item[3] / accumulation * 100
                else:
                    labels.append (item[0]) # hostname
                    val.append (item[3] / accumulation * 100)
        
        # Create subplots: use 'domain' type for Pie subplot
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        if hostname and not username:
            fig.add_trace(go.Pie(labels=labels, values=val, name=hostname), 1, 1)
        if username and not hostname:
            fig.add_trace(go.Pie(labels=labels, values=val, name=username), 1, 1)

        # Use `hole` to create a donut-like pie chart
        fig.update_traces(hole=.4, hoverinfo="label+percent+name")

        if hostname and not username:
            fig.update_layout(
                title_text="Usage Report for " + hostname,
                # Add annotations in the center of the donut pies.
                annotations=[dict(text=hostname, x=0.18, y=0.5, font_size=20, showarrow=False)])
        if username and not hostname:
            fig.update_layout(
                title_text="Usage Report for " + username,
                # Add annotations in the center of the donut pies.
                annotations=[dict(text=username, x=0.18, y=0.5, font_size=20, showarrow=False)])
        fig.show()
        fig.write_image(f"{directory}/fig2.png", scale=1)
    
    
    # fig.write_image(f"{directory}/fig1.png", scale=6)
    # fig.write_image(f"{directory}/fig1.png", scale=2)
    # fig_pie.write_image(f"{directory}/fig_pie.png", scale=2)
    # fig.show()



    html="""\
    <html>
    <head>
    </head>
    <body>
    <img src='https://pawsey.org.au/wp-content/themes/project/img/pawsey-logo-beige.png' style='width: 150px'>
    <table style="border-collapse:collapse;border-spacing:0;">
        <thead>
            <tr>
                <td colspan='1' style='background-color:#4caf4f66; text-align:center; font-weight:bold; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;'>Node</td>
                <td colspan='3' style='background-color:#af4c7166; text-align:center; font-weight:bold; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;'>General Partition</td>
                <td colspan='5' style='background-color:#4c8faf87; text-align:center; font-weight:bold; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;'>Identification</td>
            </tr>
        </thead>
        <thead style='background-color: #80808073'>
            <tr style='text-align: left;'>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">Hostname</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">Start</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">End</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">Duration</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">User</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">Email</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">FirstN</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">LastN</td>              
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">Institute</td>              
            </tr>
        </thead>
        {% for title in titles %}
            {% if title[0] % 2 == 0 %}
                <tr style="background-color: #ecf5fb">
            {% else %}
                <tr>
            {% endif %}
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[1]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[2]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[3]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[4]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[6]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[7]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[8]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[9]}}</td>
                <td style="font-family:Arial, sans-serif; font-size:14px; padding:10px 5px; border-style:solid; border-width:1px; overflow:hidden; word-break:normal; border-color:black;">{{title[10]}}</td>
            </tr>
        {% endfor %}
    </table>
    {% if file2==True %}
    <img src="cid:2">
    {% endif %}
    {% if file1==True %}
    <img src="cid:1">
    {% endif %}
    </body>
    </html>"""
    
    my_templ = Template(html)
    # # mailFunction (f"Report for {hostname} {username} {str(start)} {str(end)}", my_templ.render(titles=sentence), directory, ['fig1.png'])

    if initiate.email:
        email_with_embeded_image(my_templ.render(titles=actual_usage_report_results3_list, file1=os.path.exists(f'{directory}/fig1.png'), file2=os.path.exists(f'{directory}/fig2.png')))
        # email_with_embeded_image(actual_usage_report_results_html)
    

    # email_with_embeded_image(build_table(actual_usage_report_results, 'blue_light'))
    # # mailFunction ('subject', my_templ.render (titles=tabulate(sentence, tablefmt="html")), '', '')
    # # return  actual_usage_report_results, accumulation

    # # import smtplib

    # # from email.mime.multipart import MIMEMultipart
    # # from email.mime.text import MIMEText
    # # from email.mime.image import MIMEImage
    # # from_addr= 'noreply@pawsey.org.au'
    # # to_addr= 'ali.zamani@pawsey.org.au'
    # # msg = MIMEMultipart('alternative')
    # # msg['Subject'] = "subject"
    # # msg['From'] = from_addr
    # # msg['To'] = to_addr

    # # text = MIMEText('<h3>hi</h3><img src="cid:image1">', 'html')
    # # msg.attach(text)

    # # image = MIMEImage(open(f'{directory}/fig1.png', 'rb').read())

    # # # Define the image's ID as referenced in the HTML body above
    # # image.add_header('Content-ID', '<image1>')
    # # msg.attach(image)

    # # s = smtplib.SMTP('mail-server.pawsey.org.au')
    # # s.sendmail(from_addr, to_addr, msg.as_string())
    # # s.quit()


  


    # # except:
    # #     print (f"error: records for < {hostname} >, < {username} >, < {start} >, < {end} > was not found in report database") if MyPrintCondition.fprint else 0
    # #     logger.error(f"records for < {hostname} >, < {username} >, < {start} >, < {end} > was not found in report database")