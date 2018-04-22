# 个人微博与微博话题抓取

* user_info.py是个人所有微博的抓取
* huati.py为对微博关键字话题的抓取
* weibo_clean.py  为对用户所发微博清空
* 雾霾.xls是测试采集的数据

*  页面只展示100也得内容，实际测试可以拿到199页的内容
![](https://github.com/duolaAOA/weibo_topic/blob/master/topic.png?raw=true)


## 2018.4.20 
## Python 版本
- `python`: 3.6.4

## huati.py 变量名的说明
|     变量名      |        作用        |
| :-------------: | :----------------: |
|    weibo_id     |      微博文章id  |
|    user_id      |      用户id  |
|    contents     |      用户发布内容 |
|    times        |      发送日期  |
|    praise_num     |    点赞数  |
|    transmit_num |      转发数 |
|    comment_num     |  评论数  |
|    create_time     | 微博发布时间  |


## 文件结构
* 新增settings配置文件
* 新增log日志 文件

## 功能实现

- settings.py

    1. 在settings文件中对相关参数进行填写配置


- huati.py

    1. 可选择insert_one函数单条插入

    2. 可选择insert_many函数批量插入
    
    3. 默认使用Chrome, 也可自行更改为其它浏览器驱动
    
    
- weibo_clean.py

    1. 在settings.py中配置好 USERNAME 与 PASSWORD， LOGIN_URL_COM

    2. 默认使用 WeiBoCleanCom类完成删除功能
    
    3. WeiBoCleanCom 共享 WeiBoCleanCn获取的cookie完成登录，再获取 .com域名下的cookie
    
    4. .cn域名下做删除暂时有点问题， 默认在WeiBoCleanCom中处理
    
    5. 删除时设置睡眠时间稍微大一点， 否则容易异常中断

```python3.6
# 使用
from weibo_clean import delete
delete.del_weibo()

```

