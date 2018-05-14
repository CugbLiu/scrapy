#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-08 10:35:13
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os


class Config(object):
    DEBUG = False
    SECRET_KEY = 'hard to guess'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    pass
