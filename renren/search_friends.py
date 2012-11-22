#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren() 
  renren.login(username,password)
  output=open('/home/yuebin/ericyue-libs/sns/renren_random_users','a')
  renren.search(output)
