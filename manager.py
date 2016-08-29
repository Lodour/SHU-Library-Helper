# coding=utf-8
import sys
from shulib_conn import shulib_conn


def Usage():
    print('[设置管理] python manager.py -a <address> <host> <username> <password>')
    print('[添加用户] python manager.py -u <stu_id> <password> <email>')
    print('[添加订阅] python manager.py -s <doc_number> <stu_id> <campus>')
    print('[查看帮助] python manager.py -h')

if __name__ == '__main__':
    # 连接数据库
    con, cur = shulib_conn()

    # 获取类别
    try:
        # 添加用户
        if sys.argv[1] == '-u':
            insert_sql = "insert into user values (?,?,?)"
            cur.execute(insert_sql, sys.argv[2:5])
            con.commit()

        # 设置管理
        elif sys.argv[1] == '-a':
            # 清空表
            clear_sql = "delete from sender where 1;"
            cur.execute(clear_sql)

            # 设置管理
            insert_sql = "insert into sender values (?,?,?,?);"
            cur.execute(insert_sql, sys.argv[2:6])
            con.commit()

        # 添加订阅
        elif sys.argv[1] == '-s':
            insert_sql = "insert into subscribes values (?,?,?,?);"
            cur.execute(insert_sql, sys.argv[2:5] + [''])
            con.commit()

        else:
            Usage()
    except Exception as e:
        print(e)
        Usage()
