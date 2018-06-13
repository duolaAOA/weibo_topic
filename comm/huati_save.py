# -*-coding:utf-8-*-


import pymysql
import datetime
import logging
from comm import settings


class get_Mysql(object):
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.T = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")
        # 数据库表格的名称
        self.table_name = '{}'.format(table_name)
        self.conn = pymysql.connect(
            host=settings.HOST_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWD,
            port=settings.PORT,
            db=self.db_name,
            charset='utf8'
        )

        self.cursor = self.conn.cursor()

    def create_table(self):
        sql = ''' CREATE TABLE `{tbname}` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  {weibo_id} varchar(18) NOT NULL COMMENT '微博文章id',
                  {user_id} varchar(25) NOT NULL COMMENT '用户id',
                  {contents} text COMMENT '微博内容',
                  {praise_num} int(10) NOT NULL COMMENT '点赞数',
                  {transmit_num} int(10) DEFAULT NULL COMMENT '转发数',
                  {comment_num} int(8) DEFAULT NULL COMMENT '评论数',
                  {device} varchar(20) DEFAULT NULL COMMENT '微博来自',
                  {create_time} timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '微博发布时间',
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        '''
        try:
            self.cursor.execute(sql.format(tbname=self.table_name, weibo_id='weibo_id', user_id='user_id', contents='contents', praise_num='praise_num',
                                           transmit_num='transmit_num', comment_num='comment_num', device='device', create_time='create_time'))
        except Exception as e:
            logging.warning(e)
            print('Database creation failed:', e)

        else:
            self.conn.commit()
            print('{} was created successfully.'.format(self.table_name))

    def insert(self, data):

        insert_sql = '''INSERT INTO `{tbname}`(weibo_id, user_id, contents, praise_num, 
                                                transmit_num, comment_num, device, create_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    '''
        try:
            self.cursor.execute(insert_sql.format(tbname=self.table_name),
                                (data['weibo_id'], data['user_id'], data['contents'], data['praise_num'],
                                 data['transmit_num'], data['comment_num'], data['device'],
                                 data['create_time']))
        except Exception as e:
            self.conn.rollback()
            print('Insert the failure.：', e)

        else:
            self.conn.commit()
            print('Insert a data successfully.!')

    def close_table(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    data = {'weibo_id': '1999', 'user_id': '1919949', 'contents': 'tests', 'praise_num': 11,
            'transmit_num': 12, 'comment_num': 11, 'device': '来自荣耀V8', 'create_time': '2017-09-22 19:15:08'}
    my = get_Mysql('market_price', 'ooxxooxx')
    my.create_table()
    my.insert(data)
    my.close_table()
