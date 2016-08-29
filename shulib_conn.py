#coding=utf-8
import sqlite3

def shulib_conn():
    # 数据库文件名
    db_name = './shulib.db'

    # 连接数据库
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    return con, cur
