# sends email notification for all alerts
import sys, os, smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
from vscheduler.lib.config import Credentials as MyCredentials


def mailFunction(subject, content, url, file):
    msg = MIMEMultipart()
    body = content
    msg.attach(MIMEText(body, 'plain'))

    filename = file
    if filename:
        for f in filename:
            file_path = os.path.join(url, f)
            attachment = open(file_path, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            attachment.close()
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % f)
            msg.attach(part)

    msg['Subject'] = subject
    msg['From'] = MyCredentials.email_from
    msg['To'] = MyCredentials.email_to

    sender = smtplib.SMTP(MyCredentials.email_server)
    sender.send_message(msg)            # python 3
    sender.quit()