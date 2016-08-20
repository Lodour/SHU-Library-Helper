# coding=utf-8
import sqlite3

# 数据库文件名
db_name = 'shulib.db'

# 删除库
drp_tb_shulib_sql = "drop table if exists shulib;"
drp_tb_sender_sql = "drop table if exists sender;"

# 创建库
crt_tb_shulib_sql = """
create table if not exists shulib(
  username varchar(100) unique not null,
  password varchar(100) not null,
  email varchar(100) not null
);
"""
crt_tb_sender_sql = """
create table if not exists sender(
  addr varchar(100) unique not null,
  host varchar(100) not null,
  user varchar(100) not null,
  pass varchar(100) not null
);
"""

# 连接数据库
con = sqlite3.connect(db_name)
cur = con.cursor()

# 初始化
cur.execute(drp_tb_shulib_sql)
cur.execute(crt_tb_shulib_sql)
cur.execute(drp_tb_sender_sql)
cur.execute(crt_tb_sender_sql)

# 提交
con.commit()
