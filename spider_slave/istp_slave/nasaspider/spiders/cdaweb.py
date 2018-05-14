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
import datetime 
from gridfs import *
from bs4 import BeautifulSoup
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

download_infos = Queue.Queue(20)

mongo_url = os.environ.get('DB_NAME')
rabbitmq_url = os.environ.get('RQ_NAME','localhost')
database_name = os.environ.get('DATABASE_NAME','parsed_data')
collection_name = os.environ.get('COLLECTION_NAME','test')
file_path = 'data/'
#file_path = '/home/zwgc/cdaweb_test/'
class IntermagnetSpider(RedisSpider):

    redis_key="istp:start_urls"
    redis_batch_size = 1
    
    
    def make_request_from_data(self, data):
        print "*"*20
        print data
        print '*'*20
        data = json.loads(data)
        start_time = data.get('start_date')
        end_time = data.get('end_date')
        datasource = data.get('datasource')
        datasource_temp = []
        datasource_temp.append(datasource)
        self.datasources = datasource_temp
        self.datasets = ' ' + data.get('datasets').replace(',',' ')
        s1 = start_time.split('-')
        s2 = end_time.split('-')

        self.start_date = datetime.date(int(s1[0]), int(s1[1]), int(s1[2]))  
        self.end_date = datetime.date(int(s2[0]), int(s2[1]), int(s2[2]))
        url = 'https://cdaweb.sci.gsfc.nasa.gov'
        return scrapy.Request(url=url,dont_filter=True, method="GET",)
    # def __init__(self,*args, **kwargs):
    #     super(IntermagnetSpider, self).__init__(*args, **kwargs) 
    #     start_time = kwargs.get('start_date')
    #     end_time = kwargs.get('end_date')
    #     datasource = kwargs.get('datasource')
    #     datasource_temp = []
    #     datasource_temp.append(datasource)

    #     self.datasources = datasource_temp
        
    #     self.datasets = ' ' + kwargs.get('datasets').replace(',',' ')
    #     s1 = start_time.split('-')
    #     s2 = end_time.split('-')
    #     self.start_date = datetime.date(int(s1[0]), int(s1[1]), int(s1[2]))  
    #     self.end_date = datetime.date(int(s2[0]), int(s2[1]), int(s2[2]))
   
    name = "cdaweb"
    allowed_domains = ["cdaweb.sci.gsfc.nasa.gov"]
    # start_urls = (
    #     'https://cdaweb.sci.gsfc.nasa.gov/cgi-bin/eval1.cgi', )
    # start_date = datetime.date(2016, 1, 8)
    # end_date = datetime.date(2016, 1, 10)  # 结束日期的后一天
    # datasources = ['ACE']

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


    def store_into_mongodb(self,filename,download_link,datasource,crawl_date):
        db = self.get_db()
        collection_name = self.get_collection_name()
        coll = db[collection_name]
        # file_string = bson.binary.Binary(file_string)
        coll.save({'filename':filename,'download_link':download_link,'datasource':datasource,'content':'','date':crawl_date,'download_time':''})
        
        print "File information saved successfully"

    def confirm_exist(self, filename):
        db = self.get_db()
        collection_name = self.get_collection_name()
        coll = db[collection_name]
        result = coll.find_one({"filename": filename})
        return result


   
    def start_query(self,datasource):
        header = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727'}  
        datasource_temp = []
        datasource_temp.append(datasource)
        group = datasource_temp
        data = {'group':group,'index':'sp_phys'}
        query_url = "https://cdaweb.sci.gsfc.nasa.gov/cgi-bin/eval1.cgi"
        try:
            r = requests.post(query_url, data=data, headers=header)

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout) as e:
            r = requests.post(query_url, data=data, headers=header)
        return r.content

    def get_datasets(self):
        if self.datasets is not None:
            return self.datasets
        else:
            print 'datasets is None...'


    def final_parse(self,datasets,crawl_date):
        year = crawl_date[0:4]
        month = crawl_date[5:7]
        day = crawl_date[8:]
        str1 = '00:00:00.000'
        str2 = '23:59:59.999'
        start_time = year+'/'+month+'/'+day +" " + str1
        stop_time = year+'/'+month+'/'+day +" " + str2
       
        header = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727',\
        'Content-Type':'application/x-www-form-urlencoded'}  
    
        query_url = "https://cdaweb.sci.gsfc.nasa.gov/cgi-bin/eval3.cgi"
        data = {
        'dataset':datasets,
        'index':'sp_phys',
        'start':start_time,
        'stop':stop_time,
        'spinner':'1',
        'autoChecking': 'on',
        'action': 'get'
        }
        try:
            r = requests.post(query_url, data=data, headers=header)
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout) as e:
            r = requests.post(query_url, data=data, headers=header)
        return r.content

    def get_download_link(self,content):
        soup = BeautifulSoup(content,"lxml")
        base_url = 'https://cdaweb.sci.gsfc.nasa.gov'
        link = soup.find('a',text='Combined CDFs')
        final_url = base_url + link.get('href')
        return final_url

    def generate_date(self, start_date,end_date):
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

    def get_filename(self,start_time,data_source):
        year = start_time[0:4]
        month = start_time[5:7]
        day = start_time[8:]
        return data_source + '_' + year + '_' + month + '_' + day +'.tar.gz'

    def final_crawl(self,crawl_date,datasource):
        # content = self.start_query(datasource)
        # datasets = self.get_datasets(content)
        datasets = self.get_datasets()
        contents = self.final_parse(datasets,crawl_date)
        download_link = self.get_download_link(contents)
        filename = self.get_filename(crawl_date,datasource)
        flag = self.confirm_exist(filename)

        if flag is None:
            print "File does not exist, begin to download..." 
            self.store_into_mongodb(filename,download_link,datasource,crawl_date)
            info = {
            'download_link':download_link,
            'filename':filename,
            'collection_name':self.get_collection_name()
            }
            download_infos.put(info)
        else:
            print "File exists in MongoDB, send message to analysis module...."

   
    def parse(self, response):
        print '----------------'
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
        for datasource in self.datasources:
            print '======================crawl_datasource=================='
            print '======================' + datasource + '=============='
            for crawl_date in datelist:
                print '======================crawl_date=================='
                print '======================' + crawl_date + '=============='
                self.final_crawl(crawl_date,datasource)
                if download_infos.qsize() >= start_size and start_flag == 1:
                    print "*"*30
                    print "consumer start...."
                    print "*"*30
                    for x in range(5):
                        cu[x].start()
                    start_flag = 0
                
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

        channel.queue_declare(queue='istp_queue', durable=True)

        message = json.dumps(file_info)
        channel.basic_publish(
            exchange='', routing_key='istp_queue',
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
                   # os.remove(save_path)
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

    def get_send_message(self,database_name,collection_name,filename):
        message = {
            'database': database_name,
            'collection': collection_name+'.chunks',
            'file_name': filename,
            'collection_files':collection_name+'.files'
        }
        return message

    def save_file(self, save_path, filename, collection_name,download_time):
       
        file_string = self.get_file_string(save_path)
        db = self.get_db()
        fs = GridFS(db,collection_name)
        coll = db[collection_name]
        print '======================================='
        print filename
        print '======================================='
        result = coll.find_one({'filename': filename})
        if result is not None:
            
            result['content'] = bson.binary.Binary(file_string)
  
            try:
                flag = fs.find_one({'file_name':filename})
                if flag is None:
                    fs.put(file_string,filename=filename)
                result['download_time'] = download_time
                result['content'] = 'ok'
                coll.save(result)
            except Exception as e:
                print 'save failed......'
            try:
                message = self.get_send_message(database_name, collection_name, filename)
                response = self.produce_message(message)
                # print 'the message has been sent...'
            except Exception as e:
                pass
                # print 'send message error......'
            os.remove(save_path)
            print file_path + ' has been removed.....'
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
            filename = info['filename']
            collection_name = info['collection_name']
            save_path = self.download_file(
                download_link, filename)
            now = datetime.datetime.now()

            download_time = now.strftime('%Y-%m-%d %H:%M:%S') 
            # file_size = os.path.getsize(file_path + download_name)
            # statinfo = os.stat(file_path + download_name)
            # create_time = statinfo.st_mtime
            # timeArray = time.localtime(create_time)
            # create_date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            try:
                self.save_file(
                    save_path, filename, collection_name,download_time)
            except Exception as e:
                print "*"*30
                print e.message
                print 'failed........'
                print "*"*30

            download_infos.task_done()

if __name__ == '__main__':
    pass
