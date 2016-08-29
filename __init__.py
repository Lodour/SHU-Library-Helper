# coding=utf-8
from shulib_conn import shulib_conn


class AbstractTableInitializer(object):
    drp_tb_sql = str()
    crt_tb_sql = str()
    ist_tb_sql = str()

    @classmethod
    def run(self, cur):
        cur.execute(self.drp_tb_sql)
        cur.execute(self.crt_tb_sql)


class init_user(AbstractTableInitializer):
    drp_tb_sql = "drop table if exists user;"
    crt_tb_sql = """
        create table if not exists user(
          username varchar(100) unique not null,
          password varchar(100) not null,
          email varchar(100) not null
        );
        """


class init_sender(AbstractTableInitializer):
    drp_tb_sql = "drop table if exists sender;"
    crt_tb_sql = """
        create table if not exists sender(
          addr varchar(100) unique not null,
          host varchar(100) not null,
          user varchar(100) not null,
          pass varchar(100) not null
        );
        """


class init_subscribes(AbstractTableInitializer):
    drp_tb_sql = "drop table if exists subscribes;"
    crt_tb_sql = """
        create table if not exists subscribes(
          doc_number varchar(100) not null,
          username varchar(100) not null,
          campus varchar(100) not null,
          status varchar(100)
        );
        """


if __name__ == '__main__':
    # 连接数据库
    con, cur = shulib_conn()

    # 初始化
    queue = [var for var in vars() if var[:5] == 'init_']
    for var in queue:
        vars()[var].run(cur)

    # 提交
    con.commit()
