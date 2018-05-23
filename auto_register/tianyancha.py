import time
import requests
from selenium import webdriver
from lxml import html
from pyvirtualdisplay import Display

url = 'https://wuhan.tianyancha.com/search/p{page}?key=%E4%BA%92%E8%81%94%E7%BD%91'


class tianyancha(object):

    companny_dict = {}
    def __init__(self):
        # self.session = requests.session()
        # self.headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        #     'Connection': 'keep-alive',
        #     'Host': 'static.tianyancha.com',
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
        # }
        # self.session.headers = self.headers

        self.display = Display(visible=0,size=(1920, 1080))
        self.display.start()

        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(20)

    def search(self):
        base_url = 'https://wuhan.tianyancha.com/search/p{page}?key=%E4%BA%92%E8%81%94%E7%BD%91'
        for page in range(1,11):
            search_url = base_url.format(page=page)
            self.driver.get(search_url)
            page_source = self.driver.page_source
            if len(page_source)>1000:
                self.parse(page_source)
        self.driver.quit()
        self.display.stop()

    def parse(self,page_source):
        tree = html.fromstring(page_source.replace('<em>','').replace('</em>',''))
        node_list = tree.xpath(r'//div[@class="search_result_single search-2017 pb25 pt25 pl30 pr30 "]')
        for node in node_list:
            commpany_name= node.xpath(r'./div[2]/div[1]/a/span/text')[0].text.replace('应汉','武汉').replace('觉司','公司').replace('互未网','互联网').replace('伯入','公司')
            leader_name = node.xpath(r'./div[2]/div[2]/div[1]/div[1]/a')[0].text
            self.companny_dict[commpany_name] = leader_name



if __name__=='__main__':
    tyc = tianyancha()
    # with open('tyc.html','r') as f:
    #     page_source = f.read()
    tyc.search()
    tyc.driver.quit()
    print(tianyancha.companny_dict)