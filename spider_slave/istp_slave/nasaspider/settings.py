# -*- coding: utf-8 -*-

# Scrapy settings for intermagnet project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#


BOT_NAME = 'nasaspider'

SPIDER_MODULES = ['nasaspider.spiders']
NEWSPIDER_MODULE = 'nasaspider.spiders'

# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'nasaspider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# 增加全局并发数
CONCURRENT_REQUESTS = 100

COOKIES_ENABLED=False

LOG_LEVEL = 'INFO'

DOWNLOADER_MIDDLEWARES = {  
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':None,  
    'nasaspider.middlewares.RotateUserAgentMiddleware':400,  
}

import os

REDIS_HOST = os.environ.get("RD_NAME")
REDIS_PORT = 6379


