#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-08 10:35:13
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
from flask import Blueprint
from flask import request
from flask import jsonify

admin = Blueprint('admin',__name__)
from administor import generate_auth_token


@admin.route('/login',methods=['GET','POST'])
def login():
    print '*' * 25
    print 'now enter login...'
    print '*' * 25
    if request.method == 'POST':
        info = request.values
    else:
        info = request.args
    if info is not None:
        username = str(info.get('username'))
        password = str(info.get('password'))
        if username=='admin' and password=='123456':
            token = generate_auth_token(username)
            return jsonify({'result': 'success', 'token':token,'message': None})
        else:
            return jsonify({'result': 'error','message':u'密码错误'})
    else:
        return jsonify({'result':'error','message':u'请输入用户名和密码'})
