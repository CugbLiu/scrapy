#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-09-18 21:12:52
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from scrapy.http import Request, FormRequest
from pymongo import MongoClient
import scrapy
import socket
import re
import requests
import json
import bson.binary
import time
import datetime
import urllib2
import hashlib
import pymongo
import urllib
import sys
import os
import pika
import thread
import zipfile
import time
import Queue
import random
import threading
import shutil
from scrapy_redis.spiders import RedisSpider
import redis


default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

if not os.path.exists('data'):
    os.mkdir('data')
else:
    shutil.rmtree('data')
    os.mkdir('data')



download_infos = Queue.Queue(40)
# mongo_url = 'mongodb://172.25.88.4:27017/'
mongo_url = os.environ.get('DB_NAME')
rabbitmq_url = os.environ.get('RQ_NAME','localhost')
database_name = os.environ.get('DATABASE_NAME','downloads')
collection_name = os.environ.get('COLLECTION_NAME','intermagnet')
file_path = 'data/'
# file_path = '/home/zwgc/iaga/'

# start_date = datetime.date(1999, 1, 1)
# end_date = datetime.date(1999, 1, 5)  # 结束日期的后一天

class IntermagnetSpider(RedisSpider):

    redis_key="iaga:start_urls"
    redis_batch_size = 1
    
    def make_request_from_data(self, data):
        print "*"*20
        print data
        print '*'*20
        data = json.loads(data)
        start_time = data.get('start_date')
        end_time = data.get('end_date')
        s1 = start_time.split('-')
        s2 = end_time.split('-')
        self.start_date = datetime.date(int(s1[0]), int(s1[1]), int(s1[2]))  
        self.end_date = datetime.date(int(s2[0]), int(s2[1]), int(s2[2]))
        url = 'http://www.intermagnet.org/apps/download/php/ajax/search_catalogue.php'
        return scrapy.Request(url=url,dont_filter=True, method="GET",)
        
    # def __init__(self,*args, **kwargs):
        
    #     super(IntermagnetSpider, self).__init__(*args, **kwargs) 
    #     start_time = kwargs.get('start_date')
    #     end_time = kwargs.get('end_date')
    #     s1 = start_time.split('-')
    #     s2 = end_time.split('-')
    #     self.start_date = datetime.date(int(s1[0]), int(s1[1]), int(s1[2]))  
    #     self.end_date = datetime.date(int(s2[0]), int(s2[1]), int(s2[2]))
   
    name = "intermagnet"
    allowed_domains = ["intermagnet.org"]
    # start_urls = (
    #     'http://www.intermagnet.org/apps/download/php/ajax/search_catalogue.php', )

    rate = ''  # 'minute','second'
    data_type = ''  # 'variation','provisional','quasi-definitive','definitive'
    data_format = 'IAGA2002'
    year = ''
    month = ''
    day = ''
    region = 'America,Asia,Europe,Pacific,Africa'# 'America,Asia,Europe,Pacific,Africa'
    latid = 'NH,NM,E,SM,SH'  # 'NH,NM,E,SM,SH'
    crawl_date = ''

    def get_db(self):
        client = MongoClient(mongo_url)
        db = client[database_name]
        return db

    def get_collection_name(self):
        
        return collection_name

    def generate_date(self, start_date, end_date):
        count = int((end_date - start_date).days)
        scope = count
        total_days = scope
        dateList = []
        while scope != 0:
            date = end_date - datetime.timedelta(days=scope)
            scope = scope - 1
            # data_list.append(str(date))
            dateList.append(str(date))
        return dateList

    def start_query(self):  
        data_for_query = {
            'rate': self.rate,
            'type': self.data_type,
            'format': self.data_format,
            'from_year': self.year,
            'from_month': self.month,
            'from_day': self.day,
            'to_year': self.year,
            'to_month': self.month,
            'to_day': self.day,
            'region': self.region,  # 'America,Asia,Europe,Pacific,Africa',
            'latid': self.latid,  # 'NH,NM,E,SM,SH'
        }
        query_url = "http://www.intermagnet.org/apps/download/php/ajax/search_catalogue.php"
        try:
            r = requests.post(query_url, data=data_for_query, timeout=5)
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout) as e:
            r = requests.post(query_url, data=data_for_query, timeout=5)

        return r.content

    def get_file_info(self, content):
        res = content
        file_info = {
            'file_name': '',
            'rate': self.rate,
            'type': self.data_type,
            'format': self.data_format,
            'region': self.region,
            'latitude': self.latid,
            'date': self.crawl_date,
            'content': res
        }
        return file_info

    def get_download_link(self, url, data_for_download):
        re1 = '(\\/apps\\/download\\/products)'  # Unix Path 1
        re2 = '(\\/)'  # Any Single Character 1
        re3 = '(\\/)'  # Any Single Character 2
        re4 = '(data)'  # Word 1
        re5 = '(\\d+)'  # Integer Number 1
        re6 = '(\\.)'  # Any Single Character 3
        re7 = '(zip)'  # Word 2
        rg = re.compile(
            re1 + re2 + re3 + re4 + re5 + re6 + re7,
            re.IGNORECASE | re.DOTALL)
        url_header = 'http://www.intermagnet.org'
        try:
            socket.setdefaulttimeout(25)
            r1 = requests.post(url, data=data_for_download, timeout=5)
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout) as e:
            r1 = requests.post(url, data=data_for_download, timeout=5)
        m = rg.search(r1.content)
        if m:
            unixpath1 = m.group(1)
            c1 = m.group(2)
            c2 = m.group(3)
            word1 = m.group(4)
            int1 = m.group(5)
            c3 = m.group(6)
            word2 = m.group(7)
            temp_url = unixpath1 + c1 + c2 + word1 + int1 + c3 + word2
        final_url = url_header + temp_url
        return final_url

    def store_into_mongodb(self, file_info, file_string,
                           sha1, file_size, create_date):
        db = self.get_db()
        collection_name = self.get_collection_name()
        coll = db[collection_name]
        # file_string = bson.binary.Binary(file_string)
        coll.save(dict(
            rate=file_info['rate'],
            type=file_info['type'],
            format=file_info['format'],
            filename=file_info['file_name'],
            SHA1=sha1,
            file_size=file_size,
            create_date=create_date,
            region=file_info['region'],
            latitude=file_info['latitude'],
            date=file_info['date'],
            file_content=file_string,
            content=file_info['content']
        ))
        print "File information saved successfully"

    def confirm_exist(self, res):
        db = self.get_db()
        collection_name = self.get_collection_name()
        coll = db[collection_name]
        result = coll.find_one({"content": res})
        return result

    def get_names(self, content):
        count = 0
        file_names = ''
        for each_content in content:
            if content[each_content]['0']['available']:
                count = count + 1
                file_names = file_names + ',' + \
                    content[each_content]['0']['filename']
        file_names = file_names.lstrip(',')
        return file_names

    def final_parse(self, fileinfo, selected_names):
        file_info = fileinfo
        emails = ['968754321@qq.com','python_api@126.com','python_api@163.com','528762404@qq.com','2@qq.com','3@qq.com']
        file_url = "http://www.intermagnet.org/data-donnee/download-2-eng.php"
        data_for_download = {
            'rate': self.rate,
            'type': self.data_type,
            'format': self.data_format,
            'from_year': self.year,
            'from_month': self.month,
            'from_day': self.day,
            'to_year': self.year,
            'to_month': self.month,
            'to_day': self.day,
            'filter_region': self.region,  # 'America,Asia,Europe,Pacific,Africa',
            'filter_lat': self.latid,  # 'NH,NM,E,SM,SH'
            'select': selected_names,
            'email': emails[random.randint(0, len(emails)-1)],
            'accept': 'accept',
        }
        try:
            download_link = self.get_download_link(file_url, data_for_download)
            download_name = download_link[-22:]
            file_info['file_name'] = download_name
            # print download_link
            socket.setdefaulttimeout(20)
            info = {
            'download_link':download_link,
            'download_name':download_name,
            'collection_name':self.get_collection_name()
            }
            download_infos.put(info)
            # save_path = self.download_file(download_link, download_name)
        except socket.timeout as e:
            print "=======download time out, begin another request======"
            # os.remove(save_path)
            download_link = self.get_download_link(file_url, data_for_download)
            download_name = download_link[-22:]
            file_info['download_name'] = download_name
            print download_link
            info = {
            'download_link':download_link,
            'download_name':download_name,
            'collection_name':self.get_collection_name()
            }
            download_infos.put(info,block=True,timeout=180)
     
        file_string = ''
        file_size = ''
        sha1 = ''
        create_date = ''
        print "Current state............"
        print create_date

        self.store_into_mongodb(
            file_info,
            file_string,
            sha1,
            file_size,
            create_date)
        print '==================================='

    def generate_search_condition(self):
        types = []
        if self.rate == 'minute':
            if self.year < '2001':
                types = ['definitive']
            elif self.year < '2010':
                types = ['variation', 'definitive']
            elif self.year < '2011':
                types = ['provisional', 'variation', 'definitive']
            else:
                types = [
                    'variation',
                    'provisional',
                    'quasi-definitive',
                    'definitive']
        elif self.rate == 'second':
            if self.year < '2011':
                types = ['provisional', 'variation']
            else:
                types = ['provisional', 'variation',
                         'quasi-definitive']
        for each_type in types:
            self.data_type = each_type
            res = self.start_query()  # type(res) = str
            if res is not None:
                content = json.loads(res)  # type(content) = dict{}
            else:
                print 'The path may not be valid...'
            if 'error' not in content:
                selected_names = self.get_names(content)
                file_info = self.get_file_info(res)
                result = self.confirm_exist(res)
                if not result:
                    print "File does not exist, begin to download..."
                    self.final_parse(file_info, selected_names)
                else:
                    print "File exists in MongoDB, send message to analysis module...."
                    continue
            else:
                print "No result was found for the query, start another query..."

    def crawl_with_minute(self):
        self.rate = 'minute'
        print "---------crawl data formats of minute--------"
        try:
            self.generate_search_condition()
        except Exception as e:
            self.generate_search_condition()

    def crawl_with_second(self):
        self.rate = 'second'
        print "---------crawl data formats of second--------"
        try:
            self.generate_search_condition()
        except Exception as e:
            self.generate_search_condition()

    def parse(self, response):
        print '='*30
        print response.url
        print '='*30
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) 
        datelist = self.generate_date(self.start_date, self.end_date)
        cu = []
        for x in range(5):
            c = Consumer()
            cu.append(c)
        start_flag = 1
        days = len(datelist)
        if days > 0:
            start_size = 0
            if days <=10:
                start_size = days
            else:
                start_size = 20
            for self.crawl_date in datelist:
                print '======================crawl_date=================='
                print '======================' + self.crawl_date + '=============='
                self.year = self.crawl_date[0:4]
                self.month = self.crawl_date[5:7]
                self.day = self.crawl_date[8:]
                self.crawl_with_minute()
                
                if download_infos.qsize() >= start_size and start_flag == 1:
                    for x in range(5):
                        cu[x].start()
                    start_flag = 0

                if self.crawl_date > '2008-12-31':
                    self.crawl_with_second()

        download_infos.join()
        # shutil.rmtree('data')
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print '------------------------------------------------'
        print 'scrapy start at ' + start_time
        print 'scrapy end at ' + end_time
        print '-------------------------------------------------'


class Consumer(threading.Thread):
    """docstring for Test"""
    def __init__(self):
        threading.Thread.__init__(self)
   

    def get_db(self):
        client = MongoClient(mongo_url)
        db = client[database_name]
        return db


    def compute_SHA(self, file_string):
        sha1 = hashlib.sha1()
        sha1.update(file_string)
        fsha1 = sha1.hexdigest()
        return fsha1

    def get_file_string(self, file_path):
        f = open(file_path, 'rb')
        f.seek(0, 0)
        index = 0
        file_string = f.read()
        f.close()
        return file_string

    def produce_message(self, file_info):
        credentials = pika.PlainCredentials('admin', '123456')
        parameters = pika.ConnectionParameters(rabbitmq_url,
                                              5672,
                                              '/',
                                              credentials)

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue='iaga_queue', durable=True)

        message = json.dumps(file_info)
        channel.basic_publish(
            exchange='', routing_key='iaga_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print "============================================"
        print " [x] Sent %r" % (message,)
        print "============================================"
        time.sleep(5)
        connection.close()

    def report(self, counter, blockSize, totalSize):
        percent = int(counter * blockSize * 100 / totalSize)
        sys.stdout.write("\r%d%%" % percent + ' complete')
        sys.stdout.flush()

    def download_file(self, url, filename):
        save_path = file_path + filename
        print "file save path:"
        print save_path
        print "==============download begin=================="
        sys.stdout.write('\rFetching ' + filename + '...\n')
        print "\n第一遍写入......."
        try:
            socket.setdefaulttimeout(60)
            urllib.urlretrieve(url, save_path, reporthook=self.report)
            flag = 0
            while os.path.getsize(save_path) < 500:
                flag = flag + 1
                if flag == 5:
                    print "*"*20
                    print "The url is not available..."
                    print "*"*20
                    os.remove(save_path)
                    return

                socket.setdefaulttimeout(60)
                print "\n再次写入......."
                urllib.urlretrieve(url, save_path, reporthook=self.report)
            sys.stdout.flush()
        except (urllib2.URLError, IOError) as e:
            flag = 0
            while os.path.getsize(save_path) < 500:
                flag = flag + 1
                if flag == 5:
                    print "*"*20
                    print "The url is not available..."
                    print "*"*20
                    os.remove(save_path)
                    return
            while os.path.getsize(save_path) < 500:
                socket.setdefaulttimeout(60)
                print "\n再次写入......."
                urllib.urlretrieve(url, save_path, reporthook=self.report)
            sys.stdout.flush()
        sys.stdout.write(
            "\rDownload complete, saved as %s" %
            (filename) + '\n')
        return save_path
        # save_path = file_path + filename
        # print "file save path:"
        # print save_path
        # print "==============download begin=================="
        # sys.stdout.write('\rFetching ' + filename + '...\n')
        # print "\n第一遍写入......."
        # try:
        #     socket.setdefaulttimeout(60)
        #     urllib.urlretrieve(url, save_path, reporthook=self.report)
        #     while os.path.getsize(save_path) < 500:
        #         socket.setdefaulttimeout(60)
        #         print "\n再次写入......."
        #         urllib.urlretrieve(url, save_path, reporthook=self.report)
        #     sys.stdout.flush()
        # except (urllib2.URLError, IOError) as e:
        #     while os.path.getsize(save_path) < 500:
        #         print "\n再次写入......."
        #         socket.setdefaulttimeout(60)
        #         urllib.urlretrieve(url, save_path, reporthook=self.report)
        #     sys.stdout.flush()
        # sys.stdout.write(
        #     "\rDownload complete, saved as %s" %
        #     (filename) + '\n')
        # return save_path

    

    def save_file(self, save_path, download_name, file_size,create_date, collection_name):
        file_string = self.get_file_string(save_path)
        sha1 = self.compute_SHA(file_string)
        db = self.get_db()
        coll = db[collection_name]
        print '======================================='
        print download_name
        print '======================================='
        result = coll.find_one({'filename': download_name})
        if result is not None:
            result['file_content'] = bson.binary.Binary(file_string)
            result['SHA1'] = sha1
            result['file_size'] = file_size
            result['create_date'] = create_date
            file_info = {
                    'database': database_name,
                    'collection': collection_name,
                    'file_name': download_name
                }
                # message = file_info
            try:
                coll.save(result)
                os.remove(save_path)
                print '%s has been removed....' % save_path

                self.produce_message(file_info)
                
            except Exception as e:
                print 'failed.........'
            print 'file infomation saved successfully......'
        else:
            print 'file is not exit........'

    def run(self): 
        while True:
            global download_infos

            print '%s: trying to download files. Queue length is %d' % (threading.current_thread(), download_infos.qsize())
            # if download_infos.empty():
            #     break
            try:
                info = download_infos.get(block=True,timeout=180)
            except Exception as e:
                break
            download_link = info['download_link']
            download_name = info['download_name']
            collection_name = info['collection_name']
            save_path = self.download_file(
                download_link, download_name)
        
            file_size = os.path.getsize(file_path + download_name)
            statinfo = os.stat(file_path + download_name)
            create_time = statinfo.st_mtime
            timeArray = time.localtime(create_time)
            create_date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            try:
                self.save_file(
                    save_path, download_name, file_size,create_date, collection_name)
            except Exception as e:
                print 'failed........'
            download_infos.task_done()

if __name__ == '__main__':
    # start_date = '2011.1.1'
    # end_date = '2011.2.2'
    # try:
    #     os.system("scrapy crawl intermagnet -a start_date=%s -a end_date=%s"%(start_date,end_date))
    # except Exception as e:
    #     print e.message
    pass