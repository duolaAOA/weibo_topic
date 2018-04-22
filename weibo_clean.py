# -*-coding:utf-8 -*-

import random
import re
from lxml import etree
from datetime import datetime
import logging
import os
from time import sleep
import json
import sys

import requests
import urllib3

from huati import ChromeDrive
from comm import settings
from comm.user_agents import agents

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


"""
          github:    https://github.com/duolaAOA
          mysite:    http://140.143.18.253/
   调用方式
   >>> from weibo_clean import delete
   >>> delete.del_weibo()

    请使用 WeiBoCleanCom 处理
    WeiBoCleanCom()处理.com域名
    WeiBoCleanCn()处理.cn域名

"""


class ConfigClean(object):
    """settings 参数配置"""
    def __init__(self):

        self.cur_page = 1
        self.seed = []      # 保存发布微博编号

        self.login_url = settings.LOGIN_URL
        self.username = settings.USERNAME
        self.password = settings.PASSWORD
        self.personal_weibo = settings.PERSONAL_WEIBO
        self.personal_weibo_page = settings.PERSONAL_WEIBO_PAGE

        t = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")
        file_name = (os.path.basename(__file__)).split('.')[0]
        logging.basicConfig(level=logging.NOTSET,
                            filename='./log/{name}-{time}.log'.format(name=file_name, time=t),
                            filemode='w',
                            format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class ChromeDriverCn(ChromeDrive):

    def fetch_cookie(self, *args):
        driver = self._login(*args)
        sina_cookies = driver.get_cookies()

        cookie_item = {}
        for item in sina_cookies:
            if item.get("name") in ["SUB", "SSOLoginState"]:
                cookie_item[item.get("name")] = item.get("value")
            else:
                pass

        return cookie_item, driver


class WeiBoCleanCn(ConfigClean):
    def __init__(self):
        super(WeiBoCleanCn, self).__init__()

        self.chrome_driver_cn = ChromeDriverCn()
        cookies, self.driver = self.chrome_driver_cn.fetch_cookie(self.login_url, self.username, self.password)

        self.cookies = {"cookie": '; SUB={}; '
                        'SSOLoginState={}'.format(cookies["SUB"], cookies["SSOLoginState"])
                        }

        self.headers = {
                        'user-agent': random.choice(agents),
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'zh-CN,zh;q=0.9',
                        'upgrade-insecure-requests': '1'
                        }

    def fetch_all_weibo(self):
        """获取所有发布微博"""

        while self.cur_page < self.personal_weibo_page:

            logging.info('\n\n开始获取取第{}页\n\n'.format(self.cur_page))

            if self.cur_page > 1:
                self.headers["referer"] = self.personal_weibo.format(uid=self.get_uid(), page=self.cur_page - 1)
            else:
                self.headers["referer"] = 'https://weibo.cn/'

            publish_weibo_url = self.personal_weibo.format(uid=self.get_uid(), page=self.cur_page)
            self.cur_page += 1

            html = requests.get(url=publish_weibo_url, headers=self.headers, cookies=self.cookies).content
            selector = etree.fromstring(html, etree.HTMLParser(encoding='utf-8'))
            all_weibo = selector.xpath('//*[@class="c"]/@id')

            if not any(all_weibo):
                logging.error("未获取到微博id，请检查xpath语句或链接是否重定向!")

                raise Exception("请检查日志错误原因!")
            else:
                for i in all_weibo:
                    self.seed.append(i)

        logging.info("所有微博获取完毕!")
        return self.seed

    def get_uid(self):
        """获取用户uid"""

        uid_url = 'https://weibo.cn'
        uid_html = self.session.get(url=uid_url, headers=self.headers, cookies=self.cookies).text
        uid = re.match("(.*)(?<=href=\"\/)(.*?)/profile(.*?)", uid_html).group(2)

        return uid

    def del_weibo(self):
        """删除微博"""
        seeds = self.fetch_all_weibo()
        st = '47f176'
        for seed in seeds:
            wait_count = 0
            payload = {'type': 'del', 'id': seed, 'act': 'delc', 'rl': '1', 'st': st}
            self.headers["referer"] = "https://weibo.cn/mblog/del?id={seed}&rl=1&st={st}".format(seed=seed, st=st)

            try:
                if wait_count < 5:
                    self.session.get(url="https://weibo.cn/mblog/del", headers=self.headers,
                                     cookies=self.cookies, params=payload)
                    wait_count += 1
                else:
                    sleep(5)
                    wait_count = 0
                    self.session.get(url="https://weibo.cn/mblog/del", headers=self.headers,
                                     cookies=self.cookies, params=payload)

            except Exception:
                logging.error("{} 删除失败".format(seed))

            else:
                logging.info("{} 删除成功".format(seed))
        logging.info("所有微博删除完毕!")
        print("删除完毕")


class WeiBoCleanCom(WeiBoCleanCn):
    def __init__(self):
        super(WeiBoCleanCom, self).__init__()

        self.del_url = 'https://weibo.com/aj/mblog/del?ajwvr=6'

        self.is_existed = False

        self.login_url = settings.LOGIN_URL_COM

        self.chrome_driver_com = self.driver

        self.cookies = {"Cookie": "; SUB={};  wvr=6;".format(self.get_com_cookie()["SUB"])}

        self.headers = {
                        'user-agent': random.choice(agents),
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'zh-CN,zh;q=0.9',
                        'upgrade-insecure-requests': '1'
                        }
        self.session = requests.Session()

    def get_com_cookie(self):
        self.chrome_driver_com.get(settings.LOGIN_URL_COM)
        sina_com_cookies = self.chrome_driver_com.get_cookies()
        self.chrome_driver_com.close()

        cookie_item = {}
        for item in sina_com_cookies:
            if item.get("name") == "SUB":
                cookie_item[item.get("name")] = item.get("value")
            else:
                pass
        return cookie_item

    def _get_uid(self):
        """
        返回用户id
        :return: uid
        """

        if not self.is_existed:
            self.is_existed = True

            uid_url = 'https://weibo.com'
            uid_html = self.session.get(url=uid_url, headers=self.headers, cookies=self.cookies, verify=False).text
            uid = re.findall("'domain'\]='(.*?)'", uid_html, re.S)[0]

            return uid

        return uid_com

    def get_seed(self):
        """
        微博文章编号
        :return:  seeds
        """

        global uid_com

        uid_com = self._get_uid()

        self.headers["Referer"] = "https://weibo.com/u/{uid}?is_all=1".format(uid=uid_com)
        self.headers["Origin"] = "https://weibo.com"
        self.headers["Host"] = "weibo.com"
        self.headers["X-Requested-With"] = "XMLHttpRequest"

        try:
            seed_html = self.session.get(url="https://weibo.com/u/{uid}".format(uid=uid_com),
                                         headers=self.headers, cookies=self.cookies, verify=False).text
            seeds = re.findall('<a name=(.*?) ', seed_html, re.S)

            if not seeds:
                logging.info("所有微博删除完毕")
                print("所有微博删除完毕!")
                sys.exit()

        except AttributeError as e:
            logging.error("请检查cookies是否正确", e)
            print("请检查cookies是否正确", e)

        else:
            return seeds

    def del_weibo(self):
        """删除微博"""
        seeds = self.get_seed()
        wait_count = 0

        while seeds:

            for seed in seeds:
                form_data = {'mid': seed}
                try:

                    if wait_count < 5:

                        response = self.session.post(url=self.del_url, data=form_data,
                                                     headers=self.headers, cookies=self.cookies)
                        wait_count += 1

                        response_status = self.del_validation(response.text)

                        if response_status == "100000":
                            logging.info("{} 删除成功!".format(seed))
                            print("{} 删除成功!".format(seed))

                        else:
                            logging.info("{} 删除失败!".format(seed))
                            print("{} 删除失败!".format(seed))

                    else:
                        sleep(3)
                        wait_count = 0
                        response = self.session.post(url=self.del_url, data=form_data,
                                                     headers=self.headers, cookies=self.cookies)
                        response_status = self.del_validation(response.text)

                        if response_status == "100000":
                            logging.info("{} 删除成功!".format(seed))
                            print("{} 删除成功!".format(seed))

                        else:
                            logging.info("{} 删除失败!".format(seed))
                            print("{} 删除失败!".format(seed))

                except requests.exceptions.ConnectionError:
                    logging.info("操作频率过快,休息一下.~~zzz")
                    print("操作频率过快,休息一下.~~zzz")
                    sleep(5)
                    continue

            seeds.clear()
            print("此页删除完毕， 尝试删除下一页")

        self.del_weibo()

    @staticmethod
    def del_validation(response):
        """
        :param response:
        :return: code
        """
        status = json.loads(response)
        code = status["code"]

        return code


if __name__ == '__main__':
    delete = WeiBoCleanCom()
    delete.del_weibo()

