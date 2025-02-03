# sends email notification from clients
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def mailFunction(subject, content):
    msg = MIMEMultipart()
    body = content
    msg.attach(MIMEText(body, 'plain'))

    msg['Subject'] = subject
    msg['From'] = 'noreply@example.domain'
    msg['To'] = 'username@example.domain'

    sender = smtplib.SMTP('127.0.0.1')
    sender.send_message(msg)            # python 3
    sender.quit()