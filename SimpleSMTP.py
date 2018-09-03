#!/usr/bin/env python3

from datetime import datetime
from smtplib import SMTP_SSL
from email.utils import format_datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pytz import timezone
import configparser


class SimpleMail(object):
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.subject =""
        self.text = ""
        self.mailfrom = ""
        self.mailto = ""
        self.tmstp = None

    def send(self):
        msg = MIMEMultipart()
        msg['Date'] = self.tmstp
        msg['From'] = self.mailfrom
        msg['To'] = self.mailto
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.text))
        sender = SMTP_SSL("smtp.qq.com", 465)
        sender.login(self.username, self.passwd)
        sender.send_message(msg, self.username, self.mailto)
        sender.quit()

    def set_time(self, dt):
        self.tmstp = format_datetime(dt)

if __name__ == "__main__":
    cf = configparser.ConfigParser()
    cf.read('conf.ini')
    s = SimpleMail(cf.get('huangmenji', 'user'), cf.get('huangmenji', 'passwd'))
    s.set_time(datetime.now(timezone("PRC")))
    s.mailfrom = cf.get('huangmenji', 'user')
    s.mailto = "xxx@gmail.com"
    s.subject = "this is your offer"
    s.text = "hi bk:\n a bunch of flower"
    s.send()

