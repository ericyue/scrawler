#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren() 
  renren.set_cookie(open("COOKIE").readline().rstrip('\n'))
  renren.random_walk()
