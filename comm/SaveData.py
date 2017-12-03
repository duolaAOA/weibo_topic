#-*-coding:utf-8-*-
__author__ = 'kerberos'
__date__ = '2017/9/21 19:50 '

import pymysql
import datetime

class get_Mysql(object):
    def __init__(self,dbname,user_name):
        self.dbname = dbname
        self.T = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")
        # 数据库表格的名称
        self.table_name = '{}'.format(user_name)
        #链接数据库
        self.conn = pymysql.connect(
            host = '127.0.0.1',
            user = 'root',
            password = '1219960386',
            port = 3306,
            db = self.dbname,
            charset = 'utf8'
        )
        #获取游标

        self.cursor = self.conn.cursor()

    def create_table(self):
        sql = ''' CREATE TABLE `{tbname}` (
        {content} longtext,
        {mobile_phone} VARCHAR (20),
        {create_time} VARCHAR (25) PRIMARY KEY ,
        {crawl_time} datetime
        )
        '''
        try:
            self.cursor.execute(sql.format(tbname=self.table_name,create_time='create_time',mobile_phone='mobile_phone',content='content',crawl_time='crawl_time'))
        except Exception as e:
            print('创建表格失败，原因',e)

        else:
            self.conn.commit()
            print('创建表格成功，名称是{}'.format(self.table_name))

    def insert(self,data):
        '''插入数据，执行插入语句失败就回滚，执行成功才提交'''
        # insert_sql = '''INSERT INTO '{tbname}' VALUES('{create_time}','{mobile_phone}','{content}')'''
        # try:
        #     self.cursor.execute(insert_sql.format(tbname=self.table_name,create_time=data['create_time'],
        #                                         mobile_phone=data['mobile_phone'],content=data['content']))
        insert_sql = '''INSERT INTO weibo_慕课网_mukewang(content,mobile_phone,create_time,crawl_time) VALUES (%s, %s, %s, %s)'''
        try:
            self.cursor.execute(insert_sql,(data['content'],data['mobile_phone'],data['create_time'],data['crawl_time']))
        except Exception as e:
            self.conn.rollback()
            print('插入数据失败，原因：',e)

        else:
            self.conn.commit()
            print('成功插入一条数据！')


    #操作完成关闭游标和连接
    def close_table(self):
        self.cursor.close()
        self.conn.close()



if __name__ == '__main__':
    data = {'create_time':'09月15日 22:56','mobile_phone':'来自荣耀V8 脱影而出','content':'qwewq','crawl_time':'2017-09-22 19:15:08'}

    my = get_Mysql('sina_weibo','fgyugyujh')
    my.create_table()
    my.insert(data)
    my.close_table()
