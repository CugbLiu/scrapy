#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-08 10:35:13
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from redis_common import MyRedis
import json

main = Blueprint('main',__name__)
from myConfigure_params import my_params
mongo_url = my_params.mongo_url
mongo_port = my_params.mongo_port
database_name = my_params.database_name
collection_name = my_params.collection_name
redis_url = my_params.redis_url
redis_port = my_params.redis_port

def get_redis():
    r = MyRedis(host=redis_url, port=redis_port)
    return r

def get_datasources():
    coll = get_coll()
    datasources = []
    results = coll.find()
    for result in results:
        datasource = result.get('datasource')
        datasets = result.get('data_set')
        datasources.append({'datasource': datasource, 'datasets': datasets})
    return datasources

def get_coll():
    client = MongoClient(mongo_url, mongo_port)
    db = client[database_name]
    coll = db[collection_name]
    return coll

@main.route('/nasa', methods=['GET', 'POST'])
def scrawl_pages_istp():
    print '*' * 25
    print 'now enter scrawl...'
    print '*' * 25
    if request.method == 'POST':
        info = request.values
    else:
        info = request.args
    if info is not None:
        start_date = info.get('start_date')
        end_date = info.get('end_date')
        datasource = info.get('datasource')
        datasets = info.get('datasets')
        file_info = {
            "start_date": start_date,
            "end_date": end_date,
            "datasource": datasource,
            "datasets": datasets
        }
        r = get_redis()
        info = json.dumps(file_info)
        r.rpush("istp:start_urls", info)
        print "*" * 30
        print info
        print "*" * 30
        return 'success...'


@main.route('/intermagnet', methods=['GET', 'POST'])
def scrawl_pages_iage():
    print '*' * 25
    print 'now enter scrawl...'
    print '*' * 25
    if request.method == 'POST':
        info = request.values
    else:
        info = request.args
    if info is not None:
        start_date = str(info.get('start_date'))
        end_date = str(info.get('end_date'))

        file_info = {
            "start_date": start_date,
            "end_date": end_date
        }
        r = get_redis()
        info = json.dumps(file_info)
        r.rpush("iaga:start_urls", info)
        return 'success...'

@main.route('/datasource', methods=['GET', 'POST'])
def get_datasource():
    print '*' * 25
    print 'now enter get_datasource...'
    print '*' * 25
    datasources = get_datasources()

    return jsonify({'result': datasources})

@main.route('/redis/keys', methods=['GET'])
def get_keys():
    print '*' * 25
    print 'now enter get_keys...'
    print '*' * 25
    r = get_redis()
    result = {}
    dbsize = r.dbsize()
    keys = r.keys();
    for key in keys:
        if r.type(key) == 'list':
            result.update({key: r.lrange(key)})
        elif r.type(key) == 'string':
            result.update({key: r.get(key)})
    return jsonify({'result': result, 'count': dbsize})


@main.route('/redis', methods=['GET'])
def get_key():
    print '*' * 25
    print 'now enter get_key...'
    print '*' * 25
    info = request.args
    r = get_redis()
    if info is not None:
        print info
        try:
            key = str(info.get('key'))
        except:
            print 'error....'
        result = {}
        type = r.type(key)
        if type == 'list':
            result.update({key: r.lrange(key)})
        elif type == 'string':
            result.update({key: r.get(key)})
        return jsonify({'result': result, 'type': type})
    else:
        return jsonify({'result': 'the key is not exist....'})

@main.route('/redis', methods=['POST'])
def remove_key():
    print '*' * 25
    print 'now enter remove_key...'
    print '*' * 25
    info = request.values
    r = get_redis()
    if info is not None:
        try:
            key = str(info.get('key'))
        except:
            print  'error'
        result = r.remove(key)
        print result
        return jsonify({'result': "success"})
    else:
        return jsonify({'result': "error", 'message': 'the key is not exit...'})
