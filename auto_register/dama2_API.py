#!/usr/bin/python3.5
# coding=utf-8

# FFng, 2016-10-31, ffng0x15@gmail.com

# This is a Python interface to www.dama2.com


# software name: 3d2_v2  <-- 3大第2个，version 2
# ID: 44522
# key: 941f77b1b231f2a45ea15802248ea5ec
# USERNAME = 'cmglmz'
# PASSWORD = '6KmUqnGpBVD43WpM'


import hashlib
import requests
import base64
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os



class Dama2API:

    def __init__(self, username='11111', password='22222',
                 software_ID=102127, software_key='b35260f1f02b4488a677546060f096c8', log_file_name=''):
        self.debug = True
        self.logger = self.setup_logger(log_file_name=log_file_name)

        self.username = username
        self.password = password
        self.software_ID = software_ID
        self.software_key = software_key

    @staticmethod
    def setup_logger(logger_name='', log_file_name=''):
        logger_name = logger_name if logger_name else __name__
        log_file_name = log_file_name if log_file_name else ('./' + os.path.basename(__file__)+'.log')

        logger = logging.getLogger(name=logger_name)
        logger.setLevel(logging.DEBUG)

        # Create the console handler
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d %(levelname)s - %(module)s - %(funcName)s: %(lineno)d >>> %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Create the timed rotating file handler
        timed_rotating_file_handler = TimedRotatingFileHandler(
            filename=log_file_name,
            when='midnight',
            interval=1,
            encoding='utf-8'
        )
        timed_rotating_file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d %(levelname)s - %(module)s - %(funcName)s: %(lineno)d\n>>> %(message)s',
            datefmt='%Y-%m-%d %a %H:%M:%S'
        )
        timed_rotating_file_handler.setFormatter(file_formatter)
        logger.addHandler(timed_rotating_file_handler)

        return logger

    @staticmethod
    def md5(src=None):
        m = hashlib.md5()
        if isinstance(src, str):
            m.update(src.encode('utf-8'))
        elif isinstance(src, bytes):
            m.update(src)
        else:
            raise Exception('md5(): Unexpected type: ', type(src))

        value = m.hexdigest()
        # print('{} <-- {}'.format(value, text))
        return value

    def calc_pwd(self):
        md5 = Dama2API.md5
        pwd = md5(self.software_key + md5(md5(self.username) + md5(self.password)))
        # print('pwd: {}'.format(pwd))
        return pwd

    def calc_sign(self, param=None):
        """
        1. 查询余额： param = ''
        2. 报告结果： param = <验证码ID>
        3. 上传文件： param = <文件f.read()>
        """

        md5 = Dama2API.md5

        def byte(src):
            if isinstance(src, str):
                return bytes(src.encode('utf-8'))
            elif isinstance(src, bytes):
                return src
            else:
                raise Exception('calc_sign() -> byte(): Unexpected type: ', type(src))

        sign = md5(byte(self.software_key) + byte(self.username) + byte(param))[:8]
        # print('sign: {}, param: {}'.format(sign, param))
        return sign

    def get_balance(self):
        url = 'http://api.dama2.com:7766/app/d2Balance'
        data = {
            'appID': self.software_ID,
            'user': self.username,
            'pwd': self.pwd,
            'sign': self.calc_sign(param='')
        }
        # print(data)
        self.logger.debug('POST to get balance. username: {}'.format(self.username))
        r = requests.post(url=url, data=data)
        self.logger.info('Received response. r.status_code: {status_code}, r.json(): {json}'.format(
            status_code=r.status_code, json=r.json()
        ))
        try:
            assert r.status_code == 200, 'r.status_code != 200'
        except Exception:
            self.logger.exception('assert', exc_info=True)
            raise

        ret = r.json()
        # --> {'sign': '84825c5d', 'ret': 0, 'balance': '9960'}
        try:
            assert ret.get('ret') == 0, 'r.json().get(\'ret\') != 0'
        except Exception:
            self.logger.exception('assert', exc_info=True)
            raise

        return int(ret.get('balance'))

    def decode_captcha(self, captcha_type=-1, file_path=''):
        url = 'http://api.ruokuai.com/create.json'
        f_bin = open(file_path, 'rb').read()
        files = {'image': ('a.png', f_bin)}
        data = {
            'softid': self.software_ID,
            'softkey': self.software_key,
            'username': self.username,
            'password': self.password,
            'typeid': captcha_type,
            'timeout': 90,
        }
        headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

        self.logger.info('POST to decode CAPTCHA. captcha_type: {type}, file_path: {path}'.format(
            type=captcha_type, path=file_path
        ))
        r = requests.post(url, data=data, files=files, headers=headers)
        self.logger.info('Received r.json(): {}'.format(r.json()))
        # print(r.json())
        # --> {'result': '181,137|123,79|220,94|111,125', 'ret': 0, 'id': 1445992772, 'sign': 'cd993543'}
        # print(r.request.headers)

        ret = r.json()
        if ret.get('Error_Code') or ret.get('Result') == 'hs':
            return ret.get('Id'), []

        if captcha_type == 6137:
            coordinate_list = list(map(lambda x: tuple(map(int, x.split(','))), ret.get('Result').split('|')))
            # print(coordinate_list)
            self.logger.info(
                'CAPTCHA type: {type}, coordinate_list: {value}'.format(type=310, value=str(coordinate_list)))
            return ret.get('Id'), coordinate_list

        if captcha_type == 6900:
            # 'result': '176,142|117,79|215,96|110,122'
            # 's' --> 'step'
            # s1_str = ret.get('result')  # _'176,142|117,79|215,96|110,122'_
            # s1_str = '176,142|117,79|215,96|110,122'
            """
            s2_str_list = s1_str.split('|')  # _['176,142', '117,79', '215,96', '110,122']_
            coordinate_list = list()
            for s2_str in s2_str_list:  # s2_str: _'176,142'_
                s3_list = s2_str.split(',')
                coordinate_tuple = tuple(list(map(int, s3_list)))
                coordinate_list.append(coordinate_tuple)
            """
            """
            coordinate_list = \
                list(
                    map(
                        lambda x: tuple(map(int, x.split(','))),
                        s1_str.split('|')
                    )
                )
            """
            coordinate_list = list(map(lambda x: tuple(map(int, x.split(','))), ret.get('Result').split('.')))
            # print(coordinate_list)
            self.logger.info('CAPTCHA type: {type}, coordinate_list: {value}'.format(type=308, value=str(coordinate_list)))
            return ret.get('Id'), coordinate_list

        if captcha_type == 302:
            coordinate_list = list(map(lambda x: tuple(map(int, x.split(','))), ret.get('Result').split('|')))
            # print(coordinate_list)
            self.logger.info('CAPTCHA type: {type}, coordinate_list: {value}'.format(type=302, value=str(coordinate_list)))
            return ret.get('Id'), coordinate_list

        if captcha_type == 310:
            coordinate_list = list(map(lambda x: tuple(map(int, x.split(','))), ret.get('Result').split('|')))
            # print(coordinate_list)
            self.logger.info('CAPTCHA type: {type}, coordinate_list: {value}'.format(type=310, value=str(coordinate_list)))
            return ret.get('Id'), coordinate_list

        return ret.get('Id'), ret.get('Result')

    def report_error(self, captcha_id: str):
        if self.debug:
            pass

        url = 'http://api.ruokuai.com/reporterror.json'
        headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }
        data = {
            'id': captcha_id,
        }
        self.logger.info('POST to report error. captcha_id: {}'.format(captcha_id))
        r = requests.post(url=url, data=data, headers=headers)
        self.logger.debug('Received r.json(): {}'.format(r.json()))
        # print('report_error():\n', r.json())

        ret = r.json()
        # assert ret.get('ret') == 0


def test_debug():
    dmt = Dama2API(username=USERNAME, password=PASSWORD, software_ID=SOFTWARE_ID, software_key=SOFTWARE_KEY)
    dmt.debug = True

    # dmt.calc_pwd()
    # TEST: 05ce70090c97c9a2baec9fa45811a575
    # not TEST: 4932a06c2664a7c9934463d577e6fa2b

    # 计算用于 查询余额 的 sign
    # dmt.calc_sign(param=USERNAME)
    # TEST: 7e1c157
    # not TEST: 67866c0

    # 计算用于 报告结果 的 sign
    # dmt.calc_sign(param='test13679')
    # TEST: f113db2

    # 查询余额
    dmt.get_balance()

    # 上传 0349.bmp
    captcha_id, captcha_value = dmt.decode_captcha(captcha_type=200, file_path='0349.bmp')

    # 上传 yhyj.png
    dmt.decode_captcha(captcha_type=308, file_path='./yong_hu_yan_jiu.png')

    # 在图片上描坐标
    coordinate_list = [(181, 137), (123, 79), (220, 94), (111, 125)]
    dmt.draw_dots_on_a_picture(image_path='./yong_hu_yan_jiu.png', coordinate_list=coordinate_list)

    # 报告错误
    dmt.report_error(captcha_id=str(captcha_id))


if __name__ == '__main__':
    # TEST = True if 0 else False
    # USERNAME = 'cmglmz' if not TEST else 'name'
    # PASSWORD = '6KmUqnGpBVD43WpM' if not TEST else 'password'
    # SOFTWARE_ID = 44522
    # SOFTWARE_KEY = 'b046c3489aa04ddbb057353253a00d1a' if not TEST else 'c94984758dd79a3dfbe19e6ef46552a6'

    USERNAME = 'cmglmz'
    PASSWORD = '6KmUqnGpBVD43WpM'
    # USERNAME = 'test'
    # PASSWORD = 'test'
    SOFTWARE_ID = 44522
    SOFTWARE_KEY = '941f77b1b231f2a45ea15802248ea5ec'
    test_debug()

    # try_plt()
