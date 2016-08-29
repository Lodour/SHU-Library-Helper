# coding=utf-8
import re
import requests
from shulib_email import shulib_email
from shulib_logger import shulib_logger
from shulib_conn import shulib_conn
from shulib_tools import *


def query(doc_number, username, campus, status):
    logger.info('query(%s, %s, %s, %s)' %
                (doc_number, username, campus, status))
    # 会话
    session = requests.Session()

    # 请求
    payload = {'doc_number': doc_number}
    query_request = session.get(query_url, params=payload)

    # 获取状态
    html_content = query_request.content.decode('utf-8')
    book_status = re.findall(r'>(\d{8}|在架上)', html_content)
    book_campus = re.findall(r'分馆：</div></td>\r\n<td>(.*?)</td>', html_content)

    # 获取书名
    detail_request = session.get(detail_url, params=payload)
    html_content = detail_request.content.decode('utf-8')
    book_title = re.findall(r'<b>(.*?)<', html_content)[0]

    # 筛选出特定校区的状态
    zip_books = zip(book_status, book_campus)
    campus_status = [st for st, camp in zip_books if campus in camp]
    available = '在架上' in campus_status
    new_status = (min(campus_status), '在架上')[available]
    if new_status != status:
        return (True, book_title, new_status)
    return (False,)


def update(con, cur, doc_number, username, status):
    query_sql = "update subscribes set status='%s' where doc_number='%s' and username='%s';"
    cur.execute(query_sql % (status, doc_number, username))
    con.commit()

if __name__ == '__main__':
    # 网址
    query_url = 'http://wap.lib.shu.edu.cn/wap/items.php'
    detail_url = 'http://wap.lib.shu.edu.cn/wap/bookdetail.php'

    # 数据库
    con, cur = shulib_conn()

    # 日志
    logger = shulib_logger(filename='monitor.log')

    # 邮件系统
    sender = get_sender(cur)
    shulib = shulib_email(sender, logger)

    # 首先获取所有用户
    users = get_users(cur)

    # 搜寻每个用户的所有任务
    for user in users:
        username, email = user[0], user[2]
        books = get_user_subscribes(cur, username)
        gen = subscribe_generator()
        for book in books:
            res = query(*book)
            if res[0]:
                update(con, cur, book[0], book[1], res[2])
                gen.append(res[1], res[2], book[2])
        html = gen.generate()
        if html:
            shulib.send(email, '【上海大学图书馆】订阅图书状态变更', html)
