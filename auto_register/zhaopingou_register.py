from selenium import webdriver
from yima_api import Yima
from selenium.webdriver import ActionChains
from dama2_API import Dama2API

import time
import random
import traceback
import os
import logging
import json





class register(object):
    password = 'jianxun1302'


    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.yima = Yima(username="fbfbfbfb", password="jianxun123", project_id=18084, project_name=u"招聘狗")
        self.account = []
        self.dama2 = Dama2API()
        with open('company.json','r') as f:
            company_info = f.read()
            self.companpy = json.loads(company_info)


    def regist(self):
        regist_url = 'http://qiye.zhaopingou.com/signup'
        maxnum = 10
        attemp = 0
        while attemp<=maxnum:
            attemp+=1
            self.driver.get(regist_url)
            #获取验证码并验证
            self._process_captcha()
            self.driver.switch_to.default_content()
            # 获取账户名和密码元素
            phoneNumElement = self.driver.find_element_by_id('form_signup_name')
            pwdElement = self.driver.find_element_by_id('form_signup_psd')
            # 获取手机号
            phonenum = self.yima.generate_phone()
            # #输入账户名和密码
            for p in phonenum:
                phoneNumElement.send_keys(p)
                time.sleep(random.uniform(0, 0.3))
            try:
                self.driver.find_element_by_xpath('//p[@class="active get_verification_code rg"]').click()
            except:
                time.sleep(5)
                continue
            code = self.yima.get_message(phone=phonenum)
            if not code:
                print('code in none')
                self.yima.release_num(phonenum)
                continue
            for c in code:
                # self.driver.find_element_by_xpath('//span[@class="placeholder"]').send_keys(c)
                self.driver.find_element_by_id('form_signup_code').send_keys(c)
                time.sleep(random.uniform(0, 0.3))

            for p in self.password:
                pwdElement.send_keys(p)
                time.sleep(random.uniform(0, 0.3))

            self.driver.find_element_by_id('free_registration_btn').click()
            time.sleep(3)
            expect_url = 'http://qiye.zhaopingou.com/user/company'
            print(self.driver.current_url)
            self.account.append(phonenum)
            print(self.account)
            if self.driver.current_url==expect_url:
                #验证公司
                self.virifyCompany()
                with open('account.txt','a') as f:
                    f.write(f'{phonenum}\n')
                with open('company.json','w') as f:
                    company_info = json.dumps(self.companpy,ensure_ascii=False)
                    f.write(company_info)
            else:
                continue


    def virifyCompany(self):
        company_info = self.companpy.popitem()
        for s in company_info[0]:
            self.driver.find_element_by_css_selector('.company_name_input01').send_keys(s)
            time.sleep(random.uniform(0,0.3))
        for s in company_info[1]:
            self.driver.find_element_by_css_selector('.name_input01').send_keys(s)
            time.sleep(random.uniform(0,0.3))
        ActionChains(self.driver).click(self.driver.find_element_by_css_selector('div.md_position_input:nth-child(5) > p:nth-child(1)')).perform()
        time.sleep(0.3)
        self.driver.find_element_by_css_selector('div.md_position_input:nth-child(5) > ul:nth-child(5) > li:nth-child(1) > p:nth-child(1)').click()
        self.driver.find_element_by_css_selector('#signup_company_info').click()
        time.sleep(2)
        expect_url = 'http://qiye.zhaopingou.com/user/comProve'
        if self.driver.current_url==expect_url:
            self.loginOut()
            return True
        else:
            raise Exception

    def loginOut(self):
        attemp = 0
        while True:
            attemp+=1
            if attemp>10:
                raise Exception
            try:
                self.driver.get('http://qiye.zhaopingou.com/')
                time.sleep(1)
                self.driver.find_element_by_css_selector('div.cMain-top:nth-child(1) > div:nth-child(3)').click()
                time.sleep(0.5)
                ActionChains(self.driver).move_to_element(self.driver.find_element_by_css_selector('.account_name')).perform()
                time.sleep(1)
                self.driver.find_element_by_css_selector('#header_user_center_logout > p:nth-child(2)').click()
                time.sleep(1)
                expect_url = 'http://qiye.zhaopingou.com/'
                if self.driver.current_url==expect_url:
                    print('login out sucessfully')
                    return True
                else:
                    continue
            except:
                continue



    def _process_captcha(self):
        self.driver.switch_to.frame(self.driver.find_elements_by_tag_name('iframe')[0])
        time.sleep(3)
        self.driver.find_element_by_xpath('//span[@class="captcha-widget-text"]').click()
        time.sleep(5)
        self.driver.switch_to.default_content()
        time.sleep(3)
        # 验证码图片元素
        # self.driver.find_elements_by_tag_name("iframe")[0].screenshot('bb.png')
        self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[2])
        # 验证码区域
        captcha_xpath = '//div[@class="lc-panel"]'
        self._login_process_captcha(captcha_xpath)




    def _login_process_captcha(self,captcha_xpath):
        l = logging
        driver = self.driver
        captcha_element = driver.find_element_by_xpath(captcha_xpath)

        #验证码坐标和大小
        offset = captcha_element.location
        print('offset:',offset)
        size = captcha_element.size

        # 验证码接口
        dama2 = self.dama2

        #保存验证码图片
        shm_dir = r'/tmp/zhaopingou/'
        if os.path.exists(shm_dir) is False:
            os.makedirs(shm_dir)
        captcha_img_path = os.path.join(shm_dir, 'captcha_img_{user_id}.png'.format(user_id='333'))
        maximum = 20
        attempt = 0
        while attempt<=maximum:
            print(f'Trying to decode CAPTCHA: {attempt}/{maximum}')

            captcha_element = driver.find_element_by_xpath(captcha_xpath)
            captcha_element.screenshot(captcha_img_path)

            try:
                captcha_id, coordinate_list = dama2.decode_captcha(captcha_type=6137, file_path=captcha_img_path)
                print(f'coordinate_list:{coordinate_list}')
            except Exception as err:
                err_str = str(err)
                tb = traceback.format_exc()
                msg = f'Exception occurred when decode CAPTCHA, err: {err_str}, tb:\n{tb}'
                l.warning(msg)
                attempt+=1
                # 发生异常时先返回主页面
                continue
            for xy in coordinate_list:
                action = ActionChains(driver)
                action.move_to_element_with_offset(captcha_element, xy[0], xy[1]).click()
                action.perform()
                time.sleep(random.uniform(0.5,2))
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
            text = driver.find_element_by_xpath('//span[@class="captcha-widget-text"]').text
            if text.find('验证成功')!=-1:
                print('验证码验证成功！')
                time.sleep(random.uniform(1,2))
                return True
            else:
                driver.switch_to.default_content()
                driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[2])
                print('fail,and try it again')
                attempt+=1
                time.sleep(2)
                continue
        raise Exception
        return False


if __name__=='__main__':
    reg = register()
    reg.regist()

