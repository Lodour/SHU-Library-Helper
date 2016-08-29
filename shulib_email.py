# coding=utf-8
"""
An email model for SHU Library Helper.
Set up an email model with a specific `sender`.
@depend lib.logger
[+] sender - list(addr, host, user, pass)
    [-] `addr` Address,  like 'shulib@test.com'
    [-] `host` Hostname, like 'smtp.test.com'
    [-] `user` Username, like 'shulib@test.com'
    [-] `pass` Password, like 'password_of_shulib'
[+] logger - shulib_logger()
[+] debug_level - default = 0
    [-] 0 - Turn off debug text.
    [-] 1 - Turn on debug text.
[+] shulib_email(sender, debug_level)
[+] send(send_to, title, mail_msg)
    Send mail_msg to send_to titled `title`.
[+] send_admin(title, mail_msg)
    Send mail_msg to sender.user titled `title`.
"""

import smtplib
from email.mime.text import MIMEText
from email.header import Header


class shulib_email(object):

    def __init__(self, sender, logger, debug_level=0):
        super(shulib_email, self).__init__()

        # 发送者信息
        sender_keys = ('addr', 'host', 'user', 'pass')
        self.__sender = dict(zip(sender_keys, sender))

        # 连接邮件服务器
        try:
            self.__svr = smtplib.SMTP_SSL(host=self.__sender['host'])
            self.__svr.set_debuglevel(debug_level)
            self.__svr.login(self.__sender['user'], self.__sender['pass'])
        except Exception as e:
            msg = '连接邮件服务器失败: %s' % (e)
            logger.warn_and_quit(msg)

    # 发送邮件
    def send(self, send_to, title, mail_msg):

        # 邮件内容设置为html
        msg = MIMEText(mail_msg, 'html', 'utf-8')

        # 设置邮件主题、发送者与接受者
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = Header("SHU图书馆助手", 'utf-8')
        msg['To'] = send_to

        # 发送邮件
        try:
            self.__svr.sendmail(
                self.__sender['addr'], send_to, msg.as_string())
        except Exception as e:
            msg = '发送邮件失败: %s' % (e)
            logger.warn_and_quit(msg)

    # 发送给管理员
    def send_admin(self, title, mail_msg):
        self.send(self.__sender['user'], title, mail_msg)
