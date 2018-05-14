#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/6 15:05
# @Author  : liuligang
# @Email   : javaweb_llg@163.com
# @File    : redis_common.py

import os
class myParmas:
    def __init__(self):
        self.redis_url = os.environ.get("RD_NAME")
        self.redis_port = 6380
        self.file_url = "http://172.20.64.184"
        self.mongo_url = os.environ.get('DB_NAME')
        self.mongo_port = 27019
        self.database_name = os.environ.get('DATABASE_NAME', 'downloads')
        self.collection_name = os.environ.get('COLLECTION_NAME', 'api')
my_params = myParmas()
