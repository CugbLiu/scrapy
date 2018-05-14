#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-13 20:48:07
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import sys
import re
import urllib2
import socket
import urllib
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime 

mongo_url = os.environ.get('DB_NAME')
database_name = os.environ.get('DATABASE_NAME','downloads')
collection_name = os.environ.get('COLLECTION_NAME','api')
mongo_port = 27019

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


def start_query(datasource):
    header = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727',\
    'Content-Type':'application/x-www-form-urlencoded'}  
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
def get_rangetime(range_time_str):
    s = range_time_str.split("[Available Time Range: ")[1]
    if s == "Select dataset for details]":
        print "**"*20
        print range_time_str
        print "**"*20
        now = datetime.datetime.now()
        update_time = now.strftime('%Y-%m-%d')
        start_time = '2004-08-08'
        end_time = update_time
        return [start_time,end_time]
    time_str = s.replace(']','').split('/')
    start_year = time_str[0]
    start_month = time_str[1]
    starat_day = time_str[2][0:2]
    end_year = time_str[2][-4:]
    end_month = time_str[3]
    end_day = time_str[4][0:2]
    start_time = start_year+"-"+start_month+"-"+starat_day
    end_time = end_year+"-"+end_month+"-"+end_day
    return [start_time,end_time]
def get_datasets(content):
    # print content
    soup = BeautifulSoup(content)
    datasets = soup.find_all('label')
    data_set = []
    for temp in datasets:
        dataset = temp.find('a').string.strip()
        flag = 0
        for child in temp.children:
            flag = flag + 1
            if flag == 4:
                range_time = child.string
                available_time = get_rangetime(range_time) 
                info = []
                info.append(dataset)
                for x in available_time:
                    info.append(x)
                print "*"*20
                print info
                print "*"*20
                data_set.append(info)  
    return data_set

def get_datasources_content():
    header = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727',
            'Content-Type':'application/x-www-form-urlencoded',"Connection":"keep-alive", "Accept-Encoding":"gzip, deflate, br"}  
    query_url = "https://cdaweb.sci.gsfc.nasa.gov/index.html/"
    try:
        r = requests.get(query_url, headers=header)
    except (requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout) as e:
        r = requests.post(query_url, headers=header)
    return r.content
def save_into_mongodb(datasource,data_set):
    try:
        client = MongoClient(mongo_url,mongo_port)
        db = client[database_name]
        coll = db[collection_name]
        now = datetime.datetime.now()
        update_time = now.strftime('%Y-%m-%d %H:%M:%S') 
        coll.save({'datasource':datasource,'data_set':data_set,'update_time':update_time})
        return True
    except Exception as e:
        return False
    
def get_coll_count():
    client = MongoClient(mongo_url,mongo_port)
    db = client[database_name]
    coll = db[collection_name]
    return coll.count()


def get_datasources(content):
    soup = BeautifulSoup(content)
    filter_omin_sources = ['ACE','IMP (All)','Wind']
    filter_omin = ['OMNI_HRO_1MIN','OMNI_HRO_5MIN','OMNI2_H0_MRG1HR','OMNI_COHO1HR_MERGED_MAG_PLASMA']
    filter_gt = ['WI_OR_DEF','WI_OR_PRE','WI_AT_DEF','WI_AT_PRE','WI_K0_SPHA']
    a = soup.find('fieldset',attrs={'style':'border:0px;'})
    labels = a.find_all('label')
    for label in labels:
        datasource = label.string.strip()
        print '*'*30
        print datasource
       
        print '*'*30
        content = start_query(datasource)
        data_set = get_datasets(content)
        if datasource in filter_omin_sources:
            if datasource == 'Wind':
                filter_omin = filter_omin + filter_gt
            for x in filter_omin:
                try:
                    data_set.remove(x)  
                except Exception as e:
                    print '*'*30
                    print e.message
                    print '*'*30
                    
                
        flag = save_into_mongodb(datasource,data_set)
        if flag:
            print 'infomation saved successfully......'
        else:
            'failed...'
def start():
    result = get_coll_count()
    if result == 0:
        print '*'*30
        print "start to scrapy information..."
        print '*'*30
        content = get_datasources_content()
        get_datasources(content)
    else:
        print '*'*30
        print "The information exist...."
        print '*'*30

if __name__ == '__main__':
    content = get_datasources_content()
    get_datasources(content)
    
