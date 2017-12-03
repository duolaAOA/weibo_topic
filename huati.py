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
import json
from urllib import parse

class weibo(object):
    def __init__(self,dbname,user_name):
        self.dbname = dbname
        self.user_name = user_name
        self.cookies = {"Cookies":'_T_WM=8182bd4f0163b28af834ac49b4de156e; SUB=_2A2502NhVDeRhGeNJ7lUY8SrKwziIHXVUIvgdrDV6PUJbkdAKLVPWkW1dgTgtdK7skHPiDDrJVVOlDinyZQ..; SUHB=0nluEtu6AqpJqd; SCF=AnYsawFrTSeDfnovpInP66UAmDHKiFH2kaCkdgvIialA1PLd462iMbTGfQuCedE1rkTH2eZ-7RmlRdnI-KgYZQU'}
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
        self.mysql.create_table()
        self.data = {}

    def get_user_data(self,start_url):
        html = self.session.get(url=start_url,headers=self.headers,cookies=self.cookies).content
        selector = etree.fromstring(html,etree.HTMLParser(encoding='utf-8'))
        all_user = selector.xpath('//div[contains(@class,"c") and contains(@id,"M")]')

        for i in all_user:

            #微博发布id
            weibo_id = i.xpath('@id')[0].encode('utf-8').decode()
            # 用户id
            re_id = i.xpath('./div[1]/a[@class="nk"]/@href')[0].encode('utf-8').decode()
            user_id = re.split('/',re_id)[-1]
            #用户发布内容
            content = i.xpath('./div[1]/span[1]')[0]
            contents = content.xpath('string(.)').encode('utf-8').decode().replace('\u200b','')
            # 发送日期
            times = i.xpath('./div/span[@class="ct"]/text()')[0].encode('utf-8').decode()
            print(times)
            html_txt = i.xpath('string(.)').encode().decode('utf-8')
            if re.search('转发了',html_txt):
                praise_num = re.findall("(?<=赞\[)\d*(?=\])", html_txt)
                transmit_num = re.findall("(?<=转发\[)\d*(?=\])", html_txt)
                comment_num = re.findall("(?<=评论\[)\d*(?=\])", html_txt)
            else:
                praise_num = re.findall("(?<=赞\[)\d*(?=\])", html_txt)[0]
                transmit_num = re.findall("(?<=转发\[)\d*(?=\])", html_txt)[0]
                comment_num = re.findall("(?<=评论\[)\d*(?=\])", html_txt)[0]
            try:
                if re.search('月', times) and re.search('来自', times):
                    month_day, time, device = times.split(maxsplit=2)
                    self.data['mobile_phone'] = device
                elif re.search('月',times) and re.search('(\d+):(\d+)',times):
                    month_day, time = times.split(maxsplit=1)
                    self.data['mobile_phone'] = ''
                elif re.search('今天',times) and re.search('(\d+):(\d+)',times):
                    month_day, time, device = times.split(maxsplit=2)
                    self.data['mobile_phone'] = device
                elif re.search('分钟',times) and re.search('来自',times):
                    time, device = times.split(maxsplit=1)
                    month_day = ''
                    self.data['mobile_phone'] = device

                self.data['create_time'] = month_day +' '+ time
            except Exception as e:
                print('failure：',e)
            self.data['crawl_time'] = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
            self.data['weibo_id'] = weibo_id
            self.data['user_id'] = user_id
            self.data['contents'] = contents
            self.data['praise_num'] = praise_num
            self.data['transmit_num'] = transmit_num
            self.data['comment_num'] = comment_num
            self.mysql.insert(self.data)
        print('\n\n开始爬取第{}页\n\n'.format(page+1))

if __name__ == '__main__':
    crawl = weibo('sina_weibo', 'weibo_赵丽颖')
    page = 1
    keyword = input('请输入你要获取的话题:')
    while page < 201:
        start_url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword={}&page={}'
        crawl.get_user_data(start_url.format(parse.quote(keyword),page))
        page += 1

    print('全部抓取完成！')