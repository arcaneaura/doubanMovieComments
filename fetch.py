# -*- coding: utf-8 -*-
import os
os.chdir('/home/excited/tools/doubanMovieComments/')
print os.getcwd()
import datetime
import sys
from scraper import doubanMovieComments
import pymongo
import time
import json
import logging

client = pymongo.MongoClient('localhost', 2717)
db = client['doubancomments']
print datetime.datetime.now()
mid = sys.argv[1]
mname = sys.argv[2]

session = doubanMovieComments('huangzhiqi04@163.com','qiqi19900701','','')
total_valid = 0
data_error = 0
duplicate_cid = 0

for i in range(1,47000,20):
    index = i if i != 1 else 0
    logging.info("scanning %d to %d comments."%(index,index+20))
    comments = session.loadComments('%s'%mid,start=index)
    if len(comments) != 0 and comments != "page load error." and comments != "ConnectTimeout":
        total_valid += len(comments)
        for j in comments:
            if db['%s'%mname].find({"cid":"%s"%j['cid']}).count() == 1:
                duplicate_cid += 1
            else:
                result = db['%s'%mname].insert_one(j)
    else:
        data_error += 20
    logging.info("valid records %d"%total_valid)
    logging.info("exsisted records %d"%duplicate_cid)
    logging.info("page error failed %d records"%data_error)
    time.sleep(20)
session.logout()
print {"total_valid":total_valid,"exsisted":duplicate_cid,"data_error":data_error}
