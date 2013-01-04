#coding=utf-8
import os
from renren import Renren
import time
import random
from datetime import datetime

if __name__=="__main__":
  renren=Renren()
  renren.set_cookie(open("COOKIE").readline().rstrip('\n'))
  friends=open('/Users/ericyue/data/renren/renren_users/renren_hebut_users.dat').readlines()
  flist=[]
  for i in friends:
    flist.append(i.split('\t')[0])
  print flist
  #flist=renren.get_friends_list("295852491")
  for f in flist:
    output_path='/Users/ericyue/data/renren/hebut_users_friend_list/%s' % f
    if os.path.exists(output_path):
        print "pass one"
        continue
    try:
        mylist=renren.get_friends_list(f)
    except:
        print "privacy found"
        continue
    output=open(output_path,'w')
    for m in mylist:
        print m
        try:
            output.write("%s\t%s\t%s\n" %(m[0].encode('utf-8'),m[1].encode('utf-8'),m[2].encode('utf-8')))
        except:
            try:
                output.write("%s\t%s\tNone\n" %(m[0].encode('utf-8'),m[1].encode('utf-8')))
            except:
                continue
