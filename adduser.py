# coding=utf-8
import sqlite3
import sys

def Usage():
    print('[添加任务] python adduser.py -u <username> <password> <email>')
    print('[设置管理] python adduser.py -s <address> <host> <username> <password>')

if __name__ == '__main__':
    # 数据库文件名
    db_name = 'shulib.db'

    # 连接数据库
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # 获取类别
    try:
        # 添加任务
        if sys.argv[1] == '-u':
            insert_sql = "insert into shulib (username, password, email) values (?,?,?)"
            user, pwd, email = sys.argv[2:5]
            cur.execute(insert_sql, (user, pwd, email))
            con.commit()

        # 设置管理
        elif sys.argv[1] == '-s':
            # 清空表
            clear_sql = "delete from sender where 1;"
            cur.execute(clear_sql)

            # 设置管理
            insert_sql = "insert into sender (addr, host, user, pass) values (?,?,?,?);"
            addr, host, user, pwd = sys.argv[2:6]
            cur.execute(insert_sql, (addr, host, user, pwd))

            con.commit()
        else:
            Usage()
    except Exception as e:
        print(e)
        Usage()

        