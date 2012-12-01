#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren() 
  renren.login(open("COOKIE").readline())
  print '*'*30    
  today=str(datetime.now()).split(' ')[0]
  renren.get_new_status(today)
  #print renren.open("http://status.renren.com/GetFriendDoing.do?curpage=0").read()
