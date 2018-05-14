#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-09-05 21:32:47
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$


import urllib2
import time
import threading
import Queue

# hosts = ["http://www.baidu.com", "http://www.baidu.com", "http://www.baidu.com",
#          "http://www.baidu.com", "http://www.baidu.com"]

# start = time.time()
# queue = Queue.Queue()
# queue.put('dsaf')
# print queue.qsize()

# s = '54.2M'
# print type(s)
# print s.endswith('M')
# s = float(s.replace('M', ''))
# print s
# class ThreadURI(threading.Thread):
#     """docstring for ThreadURI"""

#     def __init__(self, queue):
#         super(ThreadURI, self).__init__()
#         self.queue = queue

#     def run(self):
#         while True:
#             host = self.queue.get()
#             print 'sadfasdf', ''
#             print host
#             print 'sdafasdfasdfas', ''
#             url = urllib2.urlopen(host)
#             print url.read(1024)
#             self.queue.task_done()


# start = time.time()


# def main():
#     th = []
#     for host in hosts:
#         queue.put(host)
#     for i in range(5):
#         t = ThreadURI(queue)
#         th.append(t)

#     for x in th:
#         x.start()
#     queue.join()


# main()
# print "Elapsed Time: %s" % (time.time() - start)
