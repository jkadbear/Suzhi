#!/usr/bin/env python3

from bs4 import BeautifulSoup as BS
from collections import defaultdict
from SimpleSMTP import SimpleMail
from datetime import datetime
from pytz import timezone
import re
import json
import os.path
import requests
import configparser


class Suzhi:
    """docstring for Suzhi"""
    def __init__(self):
        self.jiaowu_url = 'http://postinfo.tsinghua.edu.cn/f/jiaowugonggao/more'
        self.course_namepatt = re.compile('.*研究生学术与职业素养讲座课程.*')
        self.course_link = 'a[href^="http://yjsy.cic.tsinghua.edu.cn"]'
        self.history_info = 'history_info.json'

    def get_soup(self, url):
        req = requests.get(url)
        # TODO check response 200OK
        return BS(req.text, 'lxml')

    def get_infourl(self):
        soup = self.get_soup(self.jiaowu_url)
        for a in soup.select(self.course_link):
            if (self.course_namepatt.match(a.string)):
                return a.attrs['href']

    def beautify_info(self, infolist):
        subject = ''
        flag = 0
        for (i, msg) in enumerate(infolist):
            # 面授讲座第一讲：浅谈研究生创新素质培养
            if msg.startswith('面授讲座'):
                subject = msg
                flag = i + 2
                break
        new_list = infolist[-flag:] + infolist[:-flag]
        return subject, '\n'.join(new_list)

    def parse_info(self, url):
        infolist = []
        soup = self.get_soup(url)
        info_block = soup.select('#center > div > span')[0]
        for i in info_block:
            s = i.string
            if s and re.match('.*教学计划安排.*', s):
                # enough info collected
                break
            if s and s.strip():
                infolist.append(s)
        return self.beautify_info(infolist)

    def check_new(self, url):
        if not url:
            return False
        oldinfo = defaultdict(list)
        if os.path.isfile(self.history_info):
            with open(self.history_info) as f:
                oldinfo = json.load(f)
        if url in oldinfo['url']:
            # the notification is outdated
            return False
        # new info added
        oldinfo['url'].append(url)
        with open(self.history_info, 'w') as f:
            json.dump(oldinfo, f)
        return True

    def run(self):
        url = self.get_infourl()
        # if new notification was published
        # send email to inform users
        if self.check_new(url):
            subject, text = self.parse_info(url)
            # print(subject)
            # print(text)
            self.send_email(subject, text)

    def send_email(self, subject, text):
        cf = configparser.ConfigParser()
        cf.read('conf.ini')
        # conf.ini format
        # [huangmenji]
        # user = user@qq.com
        # passwd = xxxxxxxxxxxxxxxx
        # receivers = r1@gmail.com, r2@163.com, r3@qq.com
        s = SimpleMail(cf.get('huangmenji', 'user'), cf.get('huangmenji', 'passwd'))
        s.set_time(datetime.now(timezone('PRC')))
        s.mailfrom = cf.get('huangmenji', 'user')
        s.subject = subject
        s.text = text
        receivers = cf.get('huangmenji', 'receivers').split(',')
        for user in receivers:
            s.mailto = user.strip()
            s.send()

if __name__ == '__main__':
    suzhi = Suzhi()
    suzhi.run()
