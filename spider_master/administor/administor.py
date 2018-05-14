#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-08 10:35:13
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import Flask
from flask import request,redirect
from flask_cors import CORS
from flask.ext.script import Manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from get_datasource_information import start

app = Flask(__name__)
app.config.from_object('settings.TestingConfig')
from login import admin
app.register_blueprint(admin,url_prefix='/admin')
from main import main
app.register_blueprint(main,url_prefix='/main')
manager = Manager(app)
CORS(app)
from myConfigure_params import my_params
file_url = my_params.file_url

def generate_auth_token(username, expiration=600):
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'username': username})

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return None
    username = data.get('username')
    return username

@app.before_first_request
def init_mongo():
    start()

@app.before_request
def process_request():
    print '*' * 25
    print 'now enter process_request...'
    print '*' * 25
    if request.path == '/admin/login':
        return None
    else:
        if request.method == 'POST':
            info = request.values
        else:
            info = request.args
        token = info.get('token')
        username = verify_auth_token(token)
        # print '---------username----------'
        # print username
        # print '---------username----------'
        if username=='admin':
            return None
        else:
            return redirect(file_url+'/index.html')
if __name__ == '__main__':
    manager.run()
    
