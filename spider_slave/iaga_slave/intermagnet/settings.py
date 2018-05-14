# -*- coding: utf-8 -*-

# Scrapy settings for intermagnet project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'intermagnet'

# USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

DOWNLOAD_DELAY = 0.25

SPIDER_MODULES = ['intermagnet.spiders']
NEWSPIDER_MODULE = 'intermagnet.spiders'

#ITEM_PIPELINES = {'scrapy.contrib.pipeline.files.FilesPipeline': 1}

#FILE_STORE = '/home/undoingfish/Documents/INTERMAGNET'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'intermagnet (+http://www.yourdomain.com)'
ROBOTSTXT_OBEY = False

LOG_LEVEL = 'INFO'

COOKIES_ENABLED=False

DOWNLOADER_MIDDLEWARES = {  
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware':None,  
    'intermagnet.middlewares.RotateUserAgentMiddleware':400,  
}
import os

REDIS_HOST = os.environ.get("RD_NAME")
REDIS_PORT = 6379


DOWNLOAD_DELAY = 1