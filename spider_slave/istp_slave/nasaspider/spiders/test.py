#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-13 19:32:46
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from lxml import etree
from pymongo import MongoClient
import datetime
import hashlib
import bson


mongo_url = 'mongodb://localhost:27017/'
database_name = 'cdf_test'

end_date = datetime.date(2016, 1, 10)  # 结束日期的后一天
start_date = datetime.date(2016, 1, 1)


def generate_date(start_date, end_date):

    count = int((end_date - start_date).days)
    scope = count
    total_days = scope
    dateList = []
    while scope != 0:
        date = end_date - datetime.timedelta(days=scope)
        scope = scope - 1
        dateList.append(str(date))
    return dateList


def get_db():
    client = MongoClient(mongo_url)
    db = client[database_name]
    return db








def get_collection_name(crawl_date):
	return 'test'


def save_file(collection, create_date):
    db = get_db()
    coll = db[collection]
    result = coll.find(
        {'date': create_date})
    for x in result:
        print '----------------'
        x['content'] = ''

        coll.save(x)
        print 'file infomation saved successfully......'


# save_file()

if __name__ == '__main__':
    datalist = generate_date(start_date, end_date)
    for x in datalist:
        collection = get_collection_name(x)
       
        save_file(collection, str(x))
