#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren()
  renren.login(open("COOKIE").readline().rstrip('\n'))
  flist=renren.get_my_friends_list()
  print '*'*30    
  for f in flist:
    print "%s - get blog...%s    %s/%s" % (datetime.now(),f[0],flist.index(f)+1,len(flist))
    renren.get_blog(f[0])
    #time.sleep(random.randint(1,60))

