# -*-coding:utf-8-*-
# time:2017.06.18

import random
import os
from datetime import datetime
from lxml import etree
from urllib import parse
import re
import logging
import platform
from time import sleep

import requests
import dateparser
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from comm.huati_save import get_Mysql
from comm.user_agents import agents
from comm import settings


def default_chrome_path():
    # 默认浏览器驱动
    driver_dir = getattr(settings, "DRIVER_DIR", None)
    if platform.system() == "Windows":
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver.exe"))

        raise Exception("The chromedriver drive path attribute is not found.")
    else:
        if driver_dir:
            return os.path.abspath(os.path.join(driver_dir, "chromedriver"))

        raise Exception("The chromedriver drive path attribute is not found.")


class Config(object):
    """settings 参数配置"""
    def __init__(self):
        self.db_name = settings.DB_NAME
        self.table_name = settings.TABLE_NAME
        self.login_url = settings.LOGIN_URL
        self.username = settings.USERNAME
        self.password = settings.PASSWORD
        self.topic_base_url = settings.TOPIC_BASE_URL
        self.topic_keyword = settings.TOPIC_KEYWORD
        self.max_page = settings.MAX_PAGE

        t = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")
        file_name = (os.path.basename(__file__)).split('.')[0]
        logging.basicConfig(level=logging.NOTSET,
                            filename='./log/{name}-{time}.log'.format(name=file_name, time=t),
                            filemode='w',
                            format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class ChromeDrive(object):
    """
    浏览器驱动
    """
    def __init__(self, chrome_path=default_chrome_path()):
        logging.info('Starting the Chrome service')
        self.chrome_path = chrome_path

    def start_driver(self):
        try:
            driver = self.find_chromedriver()

        except WebDriverException:
            logging.error("Unable to find chromedriver, Please check the drive path.")

        else:
            return driver

    def find_chromedriver(self):
        """路径查找"""
        try:
            driver = webdriver.Chrome()

        except WebDriverException:
            try:
                driver = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=self.build_chrome_options())

            except WebDriverException:
                raise
        return driver

    def build_chrome_options(self):
        """配置启动项"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}  # 不加载图片
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.accept_untrusted_certs = True
        chrome_options.assume_untrusted_cert_issuer = True
        arguments = ['--no-sandbox', '--disable-impl-side-painting', '--disable-setuid-sandbox', '--disable-seccomp-filter-sandbox',
                     '--disable-breakpad', '--disable-client-side-phishing-detection', '--disable-cast',
                     '--disable-cast-streaming-hw-encoding', '--disable-cloud-import', '--disable-popup-blocking',
                     '--ignore-certificate-errors', '--disable-session-crashed-bubble', '--disable-ipv6',
                     '--allow-http-screen-capture', '--start-maximized']
        for arg in arguments:
            chrome_options.add_argument(arg)
        chrome_options.add_argument('--user-agent={}'.format(random.choice(agents)))
        return chrome_options

    def fetch_cookie(self, login_url, username, password):
        if login_url:
            driver = self.start_driver()
        else:
            logging.error("Please input the login url.")
            raise Exception("Please input the login url.")

        driver.get(login_url)
        sleep(5)

        driver.find_element_by_id("loginName").clear()
        driver.find_element_by_id("loginName").send_keys(username)
        driver.find_element_by_id("loginPassword").clear()
        driver.find_element_by_id("loginPassword").send_keys(password)
        driver.find_element_by_id("loginAction").click()
        sleep(5)
        sina_cookies = driver.get_cookies()
        driver.close()

        cookie_item = {}
        for item in sina_cookies:
            if item.get("name") in ["SUB", "SSOLoginState"]:
                cookie_item[item.get("name")] = item.get("value")
            else:
                pass
        return cookie_item


class FetchSinaTopic(Config):
    """
    抓取新浪微博关键词
    """
    def __init__(self):
        super(FetchSinaTopic, self).__init__()
        self.chrome_driver = ChromeDrive()
        cookies = self.chrome_driver.fetch_cookie(self.login_url, self.username, self.password)

        self.cookies = {"cookie": '; SUB={}; '
                        'SSOLoginState={}'.format(cookies["SUB"], cookies["SSOLoginState"])
                        }

        self.headers = {
                        'user-agent': random.choice(agents),
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'zh-CN,zh;q=0.9',
                        'Connection': 'keep - alive',
                        'upgrade-insecure-requests': '1'
                        }

        self.session = requests.session()
        self.mysql = get_Mysql(self.db_name, self.table_name)
        self.mysql.create_table()

    def fetch_topic_data(self, data_dict, start_page):
        data = data_dict
        start_page = start_page
        if start_page > 1:
            self.headers["referer"] = self.topic_base_url.format(parse.quote(self.topic_keyword), start_page - 1 )
        else:
            self.headers["referer"] = 'https://weibo.cn/'

        html = self.session.get(url=self.topic_base_url.format(parse.quote(self.topic_keyword), start_page),
                                headers=self.headers, cookies=self.cookies)

        if html.status_code != 200:
            #   错误重连
            count = 0
            logging.info("错误重试, 第{}次".format(count + 1))
            if count < 3:
                sleep(3)
                count += 1
                return self.fetch_topic_data(data, start_page)

            else:
                pass
        else:
            # sleep(random.randint(1, 3))
            selector = etree.fromstring(html.content, etree.HTMLParser(encoding='utf-8'))
            all_topic = selector.xpath('//div[contains(@class,"c") and contains(@id,"M")]')

            for i in all_topic:

                # 微博发布id
                weibo_id = i.xpath('@id')[0].encode('utf-8').decode()
                # 用户id
                re_id = i.xpath('./div[1]/a[@class="nk"]/@href')[0].encode('utf-8').decode()
                user_id = re.split('/', re_id)[-1]
                # 用户发布内容
                content = i.xpath('./div[1]/span[1]')[0]
                contents = content.xpath('string(.)').encode('utf-8').decode().replace('\u200b', '')
                # 发送日期
                time_with_device = i.xpath('./div/span[@class="ct"]/text()')[0].encode('utf-8').decode()

                html_txt = i.xpath('string(.)').encode().decode('utf-8')
                if re.search('转发了', html_txt):
                    praise_num = int(re.findall("(?<=赞\[)\d*(?=\])", html_txt)[0])
                    transmit_num = int(re.findall("(?<=转发\[)\d*(?=\])", html_txt)[0])
                    comment_num = int(re.findall("(?<=评论\[)\d*(?=\])", html_txt)[0])
                else:
                    praise_num = int(re.findall("(?<=赞\[)\d*(?=\])", html_txt)[0])
                    transmit_num = int(re.findall("(?<=转发\[)\d*(?=\])", html_txt)[0])
                    comment_num = int(re.findall("(?<=评论\[)\d*(?=\])", html_txt)[0])

                try:
                    publish_time = datetime.now()
                    if re.search('月', time_with_device) and re.search('来自', time_with_device):
                        month_day, time, device = time_with_device.split(maxsplit=2)
                        publish_time = dateparser.parse("18-" + month_day + ' ' + time)
                        data['device'] = device
                    elif re.search('月', time_with_device) and re.search('(\d+):(\d+)', time_with_device):
                        month_day, time = time_with_device.split(maxsplit=1)
                        publish_time = dateparser.parse("18-" + month_day + ' ' + time)
                        data['device'] = ''
                    elif re.search('今天',time_with_device) and re.search('(\d+):(\d+)', time_with_device):
                        month_day, time, device = time_with_device.split(maxsplit=2)
                        publish_time = dateparser.parse(month_day + ' ' + time)
                        data['device'] = device
                    elif re.search('分钟',time_with_device) and re.search('来自', time_with_device):
                        time, device = time_with_device.split(maxsplit=1)
                        publish_time = dateparser.parse(time)
                        data['device'] = device

                    data['create_time'] = publish_time
                except Exception as e:
                    logging.error("Wrong date format!", e)

                data['weibo_id'] = weibo_id
                data['user_id'] = user_id
                data['contents'] = contents
                data['praise_num'] = praise_num
                data['transmit_num'] = transmit_num
                data['comment_num'] = comment_num
                return data

    def insert_one(self):
        """单条插入"""
        data_dict = {}
        start_page = 1
        while start_page < self.max_page:
            data_one = self.fetch_topic_data(data_dict, start_page)
            self.mysql.insert(data_one)
            logging.info('\n\n开始爬取第{}页\n\n'.format(start_page + 1))
            start_page += 1

        logging.info("Crawl over!")

    @staticmethod
    def insert_many():
        """批量插入"""
        data_list = []
        pass


if __name__ == '__main__':
    crawl = FetchSinaTopic()
    crawl.insert_one()

