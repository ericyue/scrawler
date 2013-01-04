#!/usr/bin/env python
#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren() 
  renren.load_cookie()
  flist=renren.get_friends_list('295852491')
  random.shuffle(flist)
  for f in flist:
    print "find status for :",f[0]
    renren.get_status(uid=f[0])
