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
        {weibo_id} VARCHAR (30) PRIMARY KEY ,
        {user_id} VARCHAR (30) ,
        {contents} longtext,
        {praise_num} VARCHAR (20),
        {transmit_num} VARCHAR (20),
        {mobile_phone} VARCHAR (100),
        {create_time} VARCHAR (25),
        {comment_num} VARCHAR (25),
        {crawl_time} datetime
        )
        '''
        try:
            self.cursor.execute(sql.format(tbname=self.table_name, weibo_id='weibo_id', user_id='user_id', contents='contents', praise_num='praise_num',
                                           transmit_num='transmit_num', comment_num='comment_num', mobile_phone='mobile_phone', create_time='create_time', crawl_time='crawl_time'))
        except Exception as e:
            print('创建表格失败，原因',e)

        else:
            self.conn.commit()
            print('创建表格成功，名称是{}'.format(self.table_name))

    def insert(self,data):

        insert_sql = '''INSERT INTO `{tbname}`(weibo_id,user_id,contents,images,praise_num,transmit_num,comment_num,mobile_phone,create_time,crawl_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        try:
            self.cursor.execute(insert_sql.format(tbname=self.table_name),(data['weibo_id'],data['user_id'],data['contents'],data['images'],data['praise_num'],
                                            data['transmit_num'],data['comment_num'],data['mobile_phone'],data['create_time'],data['crawl_time']))
        except Exception as e:
            self.conn.rollback()
            print('插入数据失败，原因：',e)

        else:
            self.conn.commit()
            print('成功插入一条数据！')

    def close_table(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    data = {'create_time':'09月15日 22:56','mobile_phone':'来自荣耀V8 脱影而出','content':'qwewq','crawl_time':'2017-09-22 19:15:08'}
    my = get_Mysql('weibo','fgyugyujh')
    my.create_table()
    my.insert(data)
    my.close_table()
