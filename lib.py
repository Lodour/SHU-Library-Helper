# coding=utf-8
"""
A Library Helper for http://wap.lib.shu.edu.cn
"""

import re
import requests

from shulib_logger import shulib_logger
from shulib_email import shulib_email
from shulib_conn import shulib_conn
from shulib_tools import *


def query(user_info):

    # 参数
    userid, password, send_to = user_info
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
    except Exception as err:
        msg = '用户%s登录出错: %s' % (userid, err)
        logger.warn(msg)
        return

    if '登录失败' in login_request.content.decode('utf-8'):
        msg = '用户%s登录失败' % (userid)
        logger.warn(msg)
        return

    # 获取借阅页面
    html_content = session.get(query_url).content.decode('utf-8')

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
        shulib.send_admin('【异常状态】', msg)

    # 生成邮件正文
    gen = memo_generator()
    for args in zip(book_info, date_info, price_info):
        gen.append(*args)
    html = gen.generate()

    # 发送邮件
    if not html == None:
        logger.info('确认发送邮件')
        shulib.send(send_to, '【上海大学图书馆】借阅超期提醒', html)


if __name__ == '__main__':
    # 网址
    index_url = 'http://wap.lib.shu.edu.cn'
    login_url = index_url + '/wap/login.php'
    query_url = index_url + '/wap/showloan.php'

    # 日志管理
    logger = shulib_logger()

    # 数据库
    try:
        con, cur = shulib_conn()
    except Exception as err:
        msg = '数据库连接失败: ' + str(err)
        logger.warn_and_quit(msg)

    # 获取待查询任务
    try:
        target = get_users(cur)
    except Exception as err:
        msg = '获取待查询任务失败: ' + str(err)
        logger.warn_and_quit(msg)

    # 邮件系统
    sender = get_sender(cur)
    shulib = shulib_email(sender, logger)

    # 执行任务
    for user in target:
        print('[Start]', user[0])
        query(user)
