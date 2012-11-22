#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren() 
  renren.login(username,password)
  flist=renren.get_my_friends_list()
  local=file('/home/yuebin/ericyue-libs/sns/renren_users/renren_hebut_users').readlines()
  local_list=[]
  for l in local:
    local_list.append(l.split('\t')[0])
  for l in flist:
    local_list.append(l[0])
  random.shuffle(local_list)
  local_list=local_list[:100]
  print '*'*30    
  print "Total User",len(flist)
  for f in local_list:
    print "%s - visited...%s    %s/%s" % (datetime.now(),f,local_list.index(f)+1,len(local_list))
    renren.visit(f)
    time.sleep(random.randint(1,60))

