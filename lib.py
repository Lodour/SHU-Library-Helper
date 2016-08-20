# coding=utf-8
"""
A Library Helper for http://www.lib.shu.edu.cn
"""

import re
import sqlite3
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header


class shulib_email(object):

    def __init__(self, sender):
        super(shulib_email, self).__init__()

        # 发送者信息
        self.__sender = {
            'addr': sender[0],
            'host': sender[1],
            'user': sender[2],
            'pass': sender[3],
        }

        # 连接邮件服务器
        self.__svr = smtplib.SMTP_SSL(host=self.__sender['host'])
        # self.__svr.set_debuglevel(1)
        self.__svr.login(self.__sender['user'], self.__sender['pass'])

    # 发送邮件
    def send(self, send_to, mail_msg):
        msg = MIMEText(mail_msg, 'html', 'utf-8')
        msg['Subject'] = Header("【上海大学图书馆】借阅超期提醒", 'utf-8')
        msg['From'] = Header("SHU图书馆助手", 'utf-8')
        msg['To'] = send_to
        self.__svr.sendmail(self.__sender['addr'], send_to, msg.as_string())


class msg_generator(object):

    def __init__(self):
        super(msg_generator, self).__init__()
        self.__msg = """
        <p>{title}</p><table cellspacing="10" class="bordered"><tr>
        <th>图书名称</th><th>应还日期</th><th>剩余天数</th><th>罚款(元)</th></tr>
        """
        self.__item = """<tr>
        <td align="center">{book}</td>
        <td align="center">{date}</td>
        <td align="center" style="{style}">{days}天</td>
        <td align="center">{price}</td></tr>
        """
        self.__msg_end = "</table>"
        self.__alert_style = "color:red;font-weight:bold;"
        self.__orange_style = "color:orange;"
        self.__green_style = "color:green;"
        self.__min_days = 1 << 60

    def append(self, book, date, price):
        book = '《{title}》'.format(title=book)
        days = msg_generator.check_date(date)
        date = '{y}-{m}-{d}'.format(y=date[0], m=date[1], d=date[2])
        self.__min_days = min(self.__min_days, days)
        if days < 0:
            style = self.__alert_style
            days = '超期%d' % (-days)
        elif days < 7:
            style = self.__orange_style
        else:
            style = self.__green_style
        if not price:
            price = '-'
        self.__msg += self.__item.format(
            book=book, date=date, style=style,
            days=days, price=price
        )

    @staticmethod
    def check_date(date_info):
        # 字符串转数字
        [YY, MM, DD] = [int(i) for i in date_info]

        # 计算时间差
        current_date = datetime.now()
        final_date = datetime(YY, MM, DD)
        return (final_date - current_date).days

    def generate(self):
        if self.__min_days < 0:
            title = '您有逾期未还的图书，请及时前往图书馆还书。'
        elif self.__min_days < 7:
            title = '您借阅的图书即将到期，请及时续借或归还。'
        else:
            title = '您借阅的图书还有%d天到期。' % (self.__min_days)
        self.__msg += self.__msg_end
        return self.__msg.format(title=title)


def query(userid, password, send_to):

    # 会话
    session = requests.Session()

    # 登录POST数据
    login_data = {
        'do': 'login',
        'userid': userid,
        'password': password,
    }

    # 登录headers
    login_headers = {
        'Referer': login_url,
    }

    # 登录
    login_request = session.post(
        url=login_url,
        data=login_data,
        headers=login_headers
    )
    if '登录失败' in login_request.content.decode('utf-8'):
        print('Login Failed.')

    # 获取借阅页面
    html_content = session.get(loan_url).content.decode('utf-8')

    # 获取信息
    book_info = re.findall(r'doc_number=\d{9}">(.*?)<', html_content)
    # code_info = re.findall(r'：(\w{9})<', html_content)
    date_info = re.findall(r'\b(\d{4})-(\d{2})-(\d{2})<', html_content)
    price_info = re.findall(r'：\s*(\d*\.\d{2})?<', html_content)

    # 检测异常
    if not len(book_info) == len(date_info) == len(price_info):
        print('Error.')

    # 生成邮件正文
    gen = msg_generator()
    for book, date, price in zip(book_info, date_info, price_info):
        gen.append(book, date, price)
    html = gen.generate()

    # 发送邮件
    shulib.send(send_to, html)


if __name__ == '__main__':
    # 网址
    index_url = 'http://wap.lib.shu.edu.cn'
    login_url = index_url + '/wap/login.php'
    loan_url = index_url + '/wap/showloan.php'

    # 数据库
    db_name = 'shulib.db'
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # 获取sender
    query_sql = "select * from sender;"
    cur.execute(query_sql)
    sender = cur.fetchall()[0]

    # 获取待查询任务
    query_sql = "select * from shulib;"
    cur.execute(query_sql)
    target = cur.fetchall()

    # 邮件系统
    shulib = shulib_email(sender)

    # 执行任务
    for user in target:
        print('[Start]', user[0])
        query(user[0], user[1], user[2])
