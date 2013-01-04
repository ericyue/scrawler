#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren()
  renren.set_cookie(open("COOKIE").readline().rstrip('\n'))
  flist=renren.get_friends_list("295852491")
  print "got my firends list:",len(flist)
  local=file('/Users/ericyue/data/renren/renren_users/renren_hebut_users.dat').readlines()
  local2=file('/Users/ericyue/data/renren/renren_users/renren_thu_female.dat').readlines() 
  local3=file('/Users/ericyue/data/renren/renren_users/renren_hebut_female.dat').readlines()
  local4=file('/Users/ericyue/data/renren/renren_bj_random_users.dat').readlines() 
  local_list=[]
  for l in local:
    tmp=l.split('\t')[0]
    if tmp not in local_list:
        local_list.append(tmp)
  for l in local2:
    tmp=l.split('\t')[0]
    if tmp not in local_list:
        local_list.append(tmp)
  for l in local3:
    tmp=l.split('\t')[0]
    if tmp not in local_list:
        local_list.append(tmp)
  for l in local4:
    tmp=l.split('\t')[0]
    if tmp not in local_list:
        local_list.append(tmp)
  for l in flist:
    if l[0] not in local_list:
        local_list.append(l[0])
  random.shuffle(local_list)
  random.shuffle(local_list)
  #local_list=local_list[:1000]
  print "Total User",len(local_list),len(set(local_list))
  for f in local_list:
    print "%s/%s" % (local_list.index(f),len(local_list))
    renren.visit(f)
    time.sleep(random.randint(0,2))
