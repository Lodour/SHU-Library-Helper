# coding=utf-8
"""
A logger model for SHU Library Helper.
Set up a logger model with filename of logfile.
Default log filename is `./shulib.log`.
[+] info(msg)
    logging.info(msg)
[+] warn(msg)
    logging.warning(msg)

[TODO] Add level-info to logging.basicConfig()
"""
import logging

class shulib_logger(object):

    def __init__(self, filename=None):
        super(shulib_logger, self).__init__()

        # 未指定文件名时，指定默认值
        if not filename:
            filename = './shulib.log'

        # 日志设置
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%F %T',
            filename=filename,
            filemode='a'
        )

    def info(self, msg):
        logging.info(msg)

    def warn(self, msg):
        logging.warn(msg)

    def warn_and_quit(self, msg):
        self.warn(msg)
        quit()
