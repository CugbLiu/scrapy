#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/6 15:05
# @Author  : liuligang
# @Email   : javaweb_llg@163.com
# @File    : redis_common.py

import os
import sys
import redis

class MyRedis:
    def __init__(self,host='localhost',port=6379,db=0):
        self.host = host
        self.port = port
        self.db = db
        pool = redis.ConnectionPool(host=self.host,port=self.port,db=self.db)
        self.r = redis.Redis(connection_pool=pool)
    #获取所有的keys
    def keys(self):
        return self.r.keys()
    def type(self,key):
        return self.r.type(key)

    def dbsize(self):
        return self.r.dbsize()

    # 1. strings 类型及操作
    # 设置 key 对应的值为 string 类型的 value
    def set(self, key, value):
        return self.r.set(key, value)

    # 设置 key 对应的值为 string 类型的 value。如果 key 已经存在,返回 0,nx 是 not exist 的意思
    def setnx(self, key, value):
        return self.r.setnx(key, value)

    # 设置 key 对应的值为 string 类型的 value,并指定此键值对应的有效期
    def setex(self, key, time, value):
        return self.r.setex(key, time, value)

    # 设置指定 key 的 value 值的子字符串
    # setrange name 8 gmail.com
    # 其中的 8 是指从下标为 8(包含 8)的字符开始替换
    def setrange(self, key, num, value):
        return self.r.setrange(key, num, value)

    # 获取指定 key 的 value 值的子字符串
    def getrange(self, key, start, end):
        return self.r.getrange(key, start, end)

    # mget(list)
    def get(self, key):
        # 批量获取
        if isinstance(key, list):
            return self.r.mget(key)
        else:
            return self.r.get(key)

    # 删除
    def remove(self, key):
        return self.r.delete(key)
    # 删除多个
    def remove_keys(self,keys):
        try:
            for key in keys:
                self.remove(key)
            return 1
        except:
            return 0
    # 自增
    def incr(self, key, default=1):
        if (1 == default):
            return self.r.incr(key)
        else:
            return self.r.incr(key, default)

    # 自减
    def decr(self, key, default=1):
        if (1 == default):
            return self.r.decr(key)
        else:
            return self.r.decr(key, default)

    # 2. hashes 类型及操作
    # 根据email获取session信息
    def hget(self, email):
        return self.r.hget('session', email)

    # 以email作为唯一标识，增加用户session
    def hset(self, email, content):
        return self.r.hset('session', email, content)

    # 获取session哈希表中的所有数据
    def hgetall(self):
        return self.r.hgetall('session')

    # 删除hashes
    def hdel(self, name, key=None):
        if (key):
            return self.r.hdel(name, key)
        return self.r.hdel(name)

    # 清空当前db
    def clear(self):
        return self.r.flushdb()

    # 3、lists 类型及操作
    # 适合做邮件队列
    # 在 key 对应 list 的头部添加字符串元素
    def lpush(self, key, value):
        return self.r.lpush(key, value)

    # 从 list 的尾部删除元素,并返回删除元素
    def lpop(self, key):
        return self.r.lpop(key)

    def rpop(self,key):
        return self.r.rpop(key)
    # 获取key对应的list元素的个数
    def llen(self, kye):
        return self.r.llen(key)

    #获取list的元素
    def lrange(self,key,start=0,end=-1):
        return self.r.lrange(key,start,end)

    def linsert(self,key ,where='BEFORE',refvalue='',value=''):
        return self.r.linsert(key,where,refvalue,value)

    def lset(self,key,index,value):
        try:
            return self.r.lset(key,index,value)
        except:
            print 'the index is error...'

    # num=0，删除列表中所有指定的值
    # num=2，从前到后，删除2个
    def lrem(self,key,value,num=0):
        return self.r.lrem(key,value,num)

if __name__ == '__main__':
    pass
    # c = MyRedis()
    # print c.set('aa','bb')
    # print c.keys()
    # print c.remove('Backup2')
    # print c.lpush("a",'3')
    # print c.lrange('lkey')
    # print c.lrange("lkey")
    # print c.remove_keys(['lkey','Backup1'])

