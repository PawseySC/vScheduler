import os, time
from pathlib import Path
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes, smtplib

def email_with_embeded_image(body):
    msg = EmailMessage()

    # generic email headers
    msg['Subject'] = 'Hello there'
    msg['From'] = 'noreply@pawsey.org.au'
    msg['To'] = 'ali.zamani@pawsey.org.au'

    # set the plain text body
    msg.set_content('This is a plain text body.')

    directory = str(Path.home()) + "/visualisation_scheduler/vscheduler/modules/reports"

    if os.path.exists(f'{directory}/fig1.png'):
    # now create a Content-ID for the image
        image_cid = make_msgid(domain='xyz.com')
        msg.add_alternative(body.format(image_cid=1), subtype='html')
    
    # if `domain` argument isn't provided, it will 
    # use your computer's name

    # set an alternative html body
    
    # msg.add_alternative("""\
    # <html>
    #     <body>
    #         <p>This is an HTML body.<br>
    #            It also has an image.
    #         </p>
    #         <img src="cid:{image_cid}">
    #     </body>
    # </html>
    # """.format(image_cid=image_cid[1:-1]), subtype='html')
    # image_cid looks like <long.random.number@xyz.com>
    # to use it as the img src, we don't need `<` or `>`
    # so we use [1:-1] to strip them off


    # now open the image and attach it to the email
    
    
        with open(f'{directory}/fig1.png', 'rb') as img:
            # know the Content-Type of the image
            maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
            # attach it
            msg.get_payload()[1].add_related(img.read(), 
                                                maintype=maintype, 
                                                subtype=subtype, 
                                                cid='1')
        
    
    if os.path.exists(f'{directory}/fig2.png'):
        image_cid2 = make_msgid(domain='xyz2.com')
        msg.add_alternative(body.format(image_cid=2), subtype='html')
        with open(f'{directory}/fig2.png', 'rb') as img_pie:
            # know the Content-Type of the image
            maintype, subtype = mimetypes.guess_type(img_pie.name)[0].split('/')
            # attach it
            msg.get_payload()[1].add_related(img_pie.read(), 
                                                maintype=maintype, 
                                                subtype=subtype, 
                                                cid='2')
    # the message is ready now
    # you can write it to a file
    # or send it using smtplib

    sender = smtplib.SMTP('mail-server.pawsey.org.au')
    sender.send_message(msg)            # python 3
    sender.quit()
    time.sleep(10)
    [os.remove(directory + "/" + file) for file in os.listdir(directory) if file.endswith('.png')]
