#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren() 
  renren.login(open("COOKIE").readline())
  output=open('./data/renren_random_users','a')
  renren.search(output)
