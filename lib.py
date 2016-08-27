# coding=utf-8
"""
A Library Helper for http://wap.lib.shu.edu.cn
"""

import re
import sqlite3
import requests
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header


class shulib_debug(object):

    def __init__(self):
        super(shulib_debug, self).__init__()

        # 日志设置
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%F %T',
            filename='./shulib.log',
            filemode='a'
        )

        self.info('日志记录启动')

    def info(self, msg):
        logging.info(msg)

    def warn(self, msg, send_mail=True):
        logging.warn(msg)
        if send_mail:
            shulib.send_admin(msg)




class shulib_email(object):

    def __init__(self, sender):
        super(shulib_email, self).__init__()

        logger.info('邮件系统启动')
        # 发送者信息
        sender_keys = ('addr', 'host', 'user', 'pass')
        self.__sender = dict(zip(sender_keys, sender))

        # 连接邮件服务器
        try:
            self.__svr = smtplib.SMTP_SSL(host=self.__sender['host'])
            self.__svr.set_debuglevel(email_debuglevel)
            self.__svr.login(self.__sender['user'], self.__sender['pass'])
        except Exception as e:
            msg = '连接邮件服务器失败: %s' % (e)
            logger.warn(msg, False)
            exit()

    # 发送邮件
    def send(self, send_to, mail_msg):

        # 邮件内容设置为html
        msg = MIMEText(mail_msg, 'html', 'utf-8')

        # 设置邮件主题、发送者与接受者
        msg['Subject'] = Header("【上海大学图书馆】借阅超期提醒", 'utf-8')
        msg['From'] = Header("SHU图书馆助手", 'utf-8')
        msg['To'] = send_to

        # 发送邮件
        try:
            self.__svr.sendmail(self.__sender['addr'], send_to, msg.as_string())
        except Exception as e:
            msg = '发送邮件失败: %s' % (e)
            logger.warn(msg, False)
            exit()

    # 发送给管理员
    def send_admin(self, mail_msg):
        self.send(self, self.__sender['user'], mail_msg)


class msg_generator(object):

    def __init__(self):
        super(msg_generator, self).__init__()

        # 邮件正文html
        self.__msg = """
        <p>{title}</p><table cellspacing="10" class="bordered"><tr>
        <th>图书名称</th><th>应还日期</th><th>剩余天数</th><th>罚款(元)</th></tr>
        """

        # 每册书籍的信息html
        self.__item = """<tr>
        <td align="center">{book}</td>
        <td align="center">{date}</td>
        <td align="center" style="{style}">{days}天</td>
        <td align="center">{price}</td></tr>
        """

        # 闭合正文html的<table>标签
        self.__msg_end = "</table>"

        # 规定三种不同的文字样式
        self.__alert_style = "color:red;font-weight:bold;"
        self.__orange_style = "color:orange;"
        self.__green_style = "color:green;"

        # 最近还书日期
        self.__min_days = 1 << 60

    # 添加一本书籍的信息
    def append(self, book, date, price):

        # 书籍标题
        book = '《{title}》'.format(title=book)

        # 计算剩余日期
        days = msg_generator.check_date(date)

        # 格式化还书日期
        date = '{0}-{1}-{2}'.format(*date)

        # 更新最近还书日期
        self.__min_days = min(self.__min_days, days)

        # 设置当前书籍的html样式
        if days < 0:
            style = self.__alert_style
            days = '超期%d' % (-days)
        elif days < 7:
            style = self.__orange_style
        else:
            style = self.__green_style

        # 未匹配到价格时，显示"-"
        if not price:
            price = '-'

        # 将变量加入html
        funtion_vars = vars()
        keys = ('book', 'date', 'style', 'days', 'price')
        kwargs = {key: funtion_vars[key] for key in keys}
        self.__msg += self.__item.format(**kwargs)

    @staticmethod
    def check_date(date_info):
        # 字符串转数字
        date_info = map(int, date_info)

        # 计算时间差
        current_date = datetime.utcnow() + UTC_to_China
        final_date = datetime(*date_info)
        return (final_date - current_date).days

    def generate(self):
        # 设置标题
        if self.__min_days < 0:
            title = '您有逾期未还的图书，请及时前往图书馆还书。'
        elif self.__min_days < 7:
            title = '您借阅的图书即将到期，请及时续借或归还。'
        else:
            # 大于一周时取消发送邮件
            title = '您借阅的图书还有%d天到期。' % (self.__min_days)
            logger.info(title)
            return None

        logger.info(title)
        self.__msg += self.__msg_end
        return self.__msg.format(title=title)


def query(user_info):

    # 参数
    [userid, password, send_to] = list(user_info)
    logger.info('query(%s)' % (userid))

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
    try:
        login_request = session.post(
            url=login_url,
            data=login_data,
            headers=login_headers
        )
    except Exception as e:
        msg = '用户%s登录出错: %s' % (userid, e)
        logger.warn(msg)
        return

    if '登录失败' in login_request.content.decode('utf-8'):
        msg = '用户%s登录失败: %s' % (userid)
        logger.warn(msg)
        return

    # 获取借阅页面
    html_content = session.get(loan_url).content.decode('utf-8')

    # 获取信息
    book_info = re.findall(r'doc_number=\d{9}">(.*?)<', html_content)
    code_info = re.findall(r'：(\w{9})<', html_content)
    date_info = re.findall(r'\b(\d{4})-(\d{2})-(\d{2})<', html_content)
    price_info = re.findall(r'：\s*(\d*\.\d{2})?<', html_content)

    # 检测异常
    if not len(book_info) == len(date_info) == len(price_info):
        msg = '检测到用户%s异常状态' % (userid)
        for i in ('book', 'date', 'price'):
            var = '%s_info' % i
            msg += '[%s] %s' % (var, repr(vars()[var]))
        logger.warn(msg)

    # 生成邮件正文
    gen = msg_generator()
    for args in zip(book_info, date_info, price_info):
        gen.append(*args)
    html = gen.generate()

    # 发送邮件
    if not html == None:
        logger.info('确认发送邮件')
        shulib.send(send_to, html)


if __name__ == '__main__':
    # 网址
    index_url = 'http://wap.lib.shu.edu.cn'
    login_url = index_url + '/wap/login.php'
    loan_url = index_url + '/wap/showloan.php'

    # 日志管理
    logger = shulib_debug()

    # 数据库
    db_name = './shulib.db'
    try:
        con = sqlite3.connect(db_name)
        cur = con.cursor()
    except Exception as e:
        msg = '数据库连接失败: %s' % (e)
        logger.warn(msg)
        exit()

    # 时差
    UTC_to_China = timedelta(hours=8)

    # 获取sender
    query_sql = "select * from sender;"
    try:
        cur.execute(query_sql)
        sender = cur.fetchall()[0]
    except Exception as e:
        msg = '获取sender失败: %s' % (e)
        logger.warn(msg)
        exit()

    # 获取待查询任务
    query_sql = "select * from shulib;"
    try:
        cur.execute(query_sql)
        target = cur.fetchall()
    except Exception as e:
        msg = '获取待查询任务失败: %s' % (e)
        logger.warn(msg)
        exit()

    # 邮件系统
    email_debuglevel = 0
    shulib = shulib_email(sender)

    # 执行任务
    for user in target:
        print('[Start]', user[0])
        query(user)
