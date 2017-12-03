#-*-coding:utf-8-*-
#time:2017.06.18

import random
from lxml import etree
import requests
from comm.user_agents import agents
from time import sleep
from comm.SaveData import get_Mysql
from datetime import datetime
import re

class weibo(object):
    def __init__(self,dbname,user_name):
        self.dbname = dbname
        self.user_name = user_name
        self.cookies = {"Cookies":'_T_WM=8182bd4f0163b28af834ac49b4de156e; SUB=_2A2502NhVDe7lUY8SrKwziIHXVUIvgdrDV6PUJbkdAKLVTgtdK7skHPiDDrJVVOlDinyZQ..; SUHB=0nluqd; SCF=AnYsawFrTSeDfnovpInP66UAmDHKiFH2kaCkdgvIialA1PLd462iMbTGfQuCedE1rkTH2eZ-7RmlRdnI-KgYZQU.; SSOLoginState=1507633157'}
        self.headers = {'User-Agent':random.choice(agents),
                        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8',
                        'Accept - Encoding': 'gzip, deflate, sdch',
                        'Accept - Language': 'zh - CN, zh;q = 0.8',
                        'Cache-Control':'max-age=0',
                        'Connection': 'keep - alive',
                        'Host':'weibo.cn',
                        'Upgrade-Insecure-Requests':'1'
                        }
        self.session = requests.session()
        self.mysql = get_Mysql(dbname,user_name)
        # self.mysql.create_table()


    def get_user_data(self,start_url):
        html = self.session.get(url=start_url,headers=self.headers,cookies=self.cookies).content
        selector = etree.fromstring(html,etree.HTMLParser(encoding='utf-8'))
        # 查找微博内容
        contents = selector.xpath('//span[@class="ctt"]/text()')
        # 发送日期
        times = selector.xpath('//span[@class="ct"]/text()')

        for each_text, each_time in zip(contents,times):
            data = {}
            data['content'] = each_text.encode().decode('utf-8').replace('\u200b','')
            try:
                if re.search('来自',each_time.encode().decode('utf-8')):
                    month_day, time, device = each_time.split(maxsplit=2)
                    data['mobile_phone'] = device
                else:
                    month_day, time = each_time.split(maxsplit=1)
                    data['mobile_phone'] = ''
                data['create_time'] = month_day +' '+ time
                data['crawl_time'] = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
                self.mysql.insert(data)
                print(data)

            except Exception as e:
                print('失败：',e)

        sleep(0.8)
        print('\n\n开始爬取第{}页\n\n'.format(i+1))


if __name__ == '__main__':
    crawl = weibo('weibo', 'weibo_210926262')
    i = 1
    while i < 1537:
        start_url = 'https://weibo.cn/u/210926262?page={}'
        crawl.get_user_data(start_url.format(i))
        i += 1


    print('全部抓取完成！')