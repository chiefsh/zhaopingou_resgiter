#!coding:utf8
import re
import requests
import time
from enum import Enum
# import asyncio
# import aiohttp
# XUNMA_STATUS = Enum("XUNMA_STATUS", "LOGIN_FAIL LOGIN_SUCCESS")
import logging

# logging.basicConfig(filename='yima_logger.log', level=logging.DEBUG)


class Yima():
    def __init__(self, token=None, project_id=None, username=None, password=None, project_name=None):
        self.session = requests.Session()
        self.token = token
        self.project_id = project_id
        self.username = username
        self.password = password
        self.project_name = project_name
        # self.session.headers = {
        #     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'Accept-Encoding':'gzip, deflate',
        #     'Accept-Language':'zh-CN,zh;q=0.9',
        #     'Cache-Control':'no-cache',
        #     'Connection':'keep-alive',
        #     'Host': 'www.xunma.net',
        #     'Pragma': 'no-cache',
        #     'Upgrade-Insecure-Requests': '1',
        #     'Referer':'https://www.baidu.com/link?url=i-ieEe8sEfV0xZxFHMCVpixK__Ais6xBV7DX4x4sooAKralOjTA3FejG3Wdbp2Wf&wd=&eqid=a61134ec0000db3e000000045a052972',
        #     'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'
        # }

    def login(self, username, password):
        retry = 0
        while True:
            retry += 1
            if retry == 10:
                logging.info("retry failed after 10 times, exit")
                raise Exception
            try:
                content = self.session.get("http://api.fxhyd.cn/UserInterface.aspx?action=login&username={}&password={}". \
                            format(username, password)).text
                logging.info(content)
                if content.find('html') > -1 :
                    #print('cookie已过期，请手动登录后重新获得')
                    #print(rUser.url)
                    continue
                self.token = content.split('|')[1]
                break
            except:
                logging.error("retry,continue get token")
                continue

    # def get_project(self, project_name):
    #     return_result = self.session.get("http://xapi.166idc.com/GetItems?token={}&tp=ut".format(self.token))
    #     content = return_result.text.split("\n")
    #     for i in content:
    #         name = i.split("&")[1]
    #         if project_name == name:
    #             self.project_id = i.split("&")[0]
    #             return 1
    #     return 0

    def get_phone_number(self, project_id=None, token=None):
        if not project_id:
            project_id = self.project_id
        if not token:
            token = self.token
        retry = 0
        while retry < 10:
            retry += 1
            try:
                result = self.session.get(
                        "http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&itemid={}&token={}"
                                .format(self.project_id, self.token)).text
            except:
                logging.error("get phone num failed, retry...")
                continue
            try:
                phone_number = result.split('|')[1]
            except:
                logging.error("extract phone num failed, retry...")
                time.sleep(3)
                continue
            return phone_number
        return ''

    def get_origin_message(self, phone_number=None,token=None, project_id=None, phone=None):
        # print(self.token, self.project_id, self.phone_number)
        try:
            result = self.session.get("http://api.fxhyd.cn/UserInterface.aspx?action=getsms&mobile={}&itemid={}&token={}". \
                                         format(phone_number, self.project_id ,self.token))
            return result.content.decode('utf-8')
        except Exception as e:
            logging.warning(str(e).replace('\n', '\\\n'))

    def generate_phone(self):
        self.login(self.username, self.password)

        phone_number = self.get_phone_number()
        logging.info(phone_number)
        # print(self.get_origin_message())
        return phone_number

    def release_num(self,phone_number=None):
        rls_url = "http://api.fxhyd.cn/UserInterface.aspx?action=release&mobile={}&itemid={}&token={}".\
            format(phone_number, self.project_id, self.token)
        result = self.session.get(rls_url).text
        if result.find('html') > -1:
            #print('cookie已过期，请手动登录后重新获得')
            #print(rms.url)
            raise Exception
        if result.find('success'):
            logging.info('已成功释放手机号:{}'.format(phone_number))
            return True

    def get_message(self,phone=None):
        for _ in range(15):
            time.sleep(5)
            text = self.get_origin_message(phone)
            logging.info("get message:{}".format(text))
            try:
                print('yanzhengmaz;',text)
                m = re.findall(r'验证码：(\d+)', text)[0]
            except:
                logging.info("extract message failed, retry...")
                continue
            else:
                result = self.release_num(phone)
                return m
        result = self.release_num(phone)
        return None


if __name__ == '__main__':
    yima = Yima(username="1111", password="22222", project_id=214, project_name=u"智联招聘")
    phone = yima.generate_phone()
    print(phone)
    yima.release_num(phone)

    # logging.info('{phone} --> {message}'.format(phone=xunma.generate_phone(), message=xunma.get_message()))


