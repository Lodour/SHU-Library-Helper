# coding=utf-8
"""
Tools for SHU Library Helper.
[+] get_sender
    Return sender.
[+] get_users
    Return all users.
[+] memo_generator
    Generate html content of an email.
"""

from datetime import datetime, timedelta


def get_sender(cur):
    query_sql = "select * from sender;"
    cur.execute(query_sql)
    return cur.fetchall()[0]


def get_users(cur):
    query_sql = "select * from user;"
    cur.execute(query_sql)
    return cur.fetchall()


def get_user_subscribes(cur, username):
    query_sql = "select * from subscribes where username = '%s';"
    cur.execute(query_sql % (username))
    return cur.fetchall()


class memo_generator(object):

    def __init__(self):
        super(memo_generator, self).__init__()

        # 邮件正文html
        self.__msg = """
        <p>{abstract}</p><table cellspacing="10" class="bordered"><tr>
        <th>图书名称</th><th>应还日期</th><th>剩余天数</th><th>罚款(元)</th></tr>
        """

        # 每册书籍的信息html
        self.__item = """<tr>
        <td align="center">{book}</td>
        <td align="ce nter">{date}</td>
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
        days = memo_generator.check_date(date)

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
        UTC_to_China = timedelta(hours=8)
        current_date = datetime.utcnow() + UTC_to_China
        final_date = datetime(*date_info)
        return (final_date - current_date).days

    def generate(self):
        # 设置摘要
        if self.__min_days < 0:
            abstract = '您有逾期未还的图书，请及时前往图书馆还书。'
        elif self.__min_days < 7:
            abstract = '您借阅的图书即将到期，请及时续借或归还。'
        else:
            # 大于一周时取消发送邮件
            abstract = '您借阅的图书还有%d天到期。' % (self.__min_days)
            return None

        self.__msg += self.__msg_end
        return self.__msg.format(abstract=abstract)

class subscribe_generator(object):

    def __init__(self):
        super(subscribe_generator, self).__init__()

        # 邮件正文html
        self.__msg = """
        <p>{abstract}</p><table cellspacing="10" class="bordered"><tr>
        <th>图书名称</th><th>应还日期</th><th>流通库</th></tr>
        """

        # 每册书籍的信息html
        self.__item = """<tr>
        <td align="center">{book}</td>
        <td align="center" style="{style}">{status}</td>
        <td align="center">{campus}</td></tr>
        """

        # 闭合正文html的<table>标签
        self.__msg_end = "</table>"

        # 规定三种不同的文字样式
        self.__alert_style = "color:red;font-weight:bold;"
        self.__orange_style = "color:orange;"
        self.__green_style = "color:green;"

        # 更新的图书数目
        self.__count = 0


    # 添加一本书籍的信息
    def append(self, book, status, campus):

        # 书籍标题
        book = '《{title}》'.format(title=book)

        if status == '在架上':
            style = self.__green_style
        else:
            style = self.__alert_style

        # 将变量加入html
        funtion_vars = vars()
        keys = ('book', 'style', 'status', 'campus')
        kwargs = {key: funtion_vars[key] for key in keys}
        self.__msg += self.__item.format(**kwargs)

        self.__count += 1

    def generate(self):
        if self.__count == 0:
            return None
        abstract = '您关注的%d本书更新了状态。' % (self.__count)
        self.__msg += self.__msg_end
        return self.__msg.format(abstract=abstract)
