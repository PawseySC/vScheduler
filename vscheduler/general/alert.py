# sends email notification for all alerts
import os, smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
from vscheduler.lib.config import Credentials


def mailFunction(subject, content, url, files):
    """
    subject = title of email
    content = email body
    url = attachment path
    files = list of attachments 
    all fields could be left blank
    """
    msg = MIMEMultipart()
    body = content
    # msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEText(body, 'html'))

    if files:
        for filename in files:
            file_path = os.path.join(url, filename)
            attachment = open(file_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            attachment.close()
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)

    msg['Subject'] = subject
    msg['From'] = Credentials.email_from
    msg['To'] = Credentials.email_to

    sender = smtplib.SMTP(Credentials.email_server)
    sender.send_message(msg)            # python 3
    sender.quit()