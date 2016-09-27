# -*- coding: utf-8 -*-
import os
os.chdir('/home/excited/Projects/doubanFetch/doubanMovieComments/')
print os.getcwd()
from scraper import doubanMovieComments
import pymongo
import time
import json
client = pymongo.MongoClient('localhost', 27017)
db = client['doubancomments']



session = doubanMovieComments('huangzhiqi04@163.com','qiqi2014521','still','QfrE78hZmRrH64mVLoCpEXIV:en')

for i in range(1001,2000,20):
    index = i if i != 1 else 0
    comments = session.loadComments('25986180',start=index)
    if len(comments) != 0:
        for j in comments:
            if db.busanhaeng.find({"cid":"%s"%j['cid']}).count() == 1:
                continue
            else:
                result = db.busanhaeng.insert_one(j)
    time.sleep(20)

session.logout()
