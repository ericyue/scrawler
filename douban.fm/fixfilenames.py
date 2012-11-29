#coding=utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding( "utf-8" )


files=os.listdir('./')
name=open('../starlist.dat').readlines()
sids={}
for n in name:
    items=n.split('\t')
    sids[items[2]+'.mp3']=items[0]+'-'+items[1]+'.mp3'
    
print "sid len",len(sids)

for f in files:
    if f[0]!='p' or f[-1]!='3':
        continue
    try:
        cmd="cp %s %s" %(f,sids[f].replace(' ','\\ ').replace("'","\\'").replace('(','\\(').replace(')','\\)'))
        print cmd 
        os.system(cmd)
    except Exception, what:
        print "pass one",what
