# -*-coding:utf-8 -*-

# 驱动路径
DRIVER_DIR = "E:/envirtual"
# 数据库名
DB_NAME = "market_price"
# 数据表名
TABLE_NAME = "test"
# 数据库地址
HOST_NAME = '127.0.0.1'
# 数据库用户名
DATABASE_USER = 'root'
# 数据库密码
DATABASE_PASSWD = ''
# 端口
PORT = 3306

# 微博登录入口
LOGIN_URL = "https://passport.weibo.cn/signin/login"
# 先获取.cn域名cookies再拿其cookies登录获取.com的cookie
LOGIN_URL_COM = "https://weibo.com"
# 登录用户名
USERNAME = ""
# 登录密码
PASSWORD = ""
# 关键词搜索入口
TOPIC_BASE_URL = "https://weibo.cn/search/mblog?hideSearchFrame=&keyword={}&page={}"
# 关键词
TOPIC_KEYWORD = "鸿茅药酒"
# 最大爬取深度
MAX_PAGE = 236

# 个人发布微博
PERSONAL_WEIBO = "https://weibo.cn/{uid}/profile?page={page}"
# 个人微博页数
PERSONAL_WEIBO_PAGE = 11
