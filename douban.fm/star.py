#coding=utf-8
import os
import time
import re
import urllib, urllib2, cookielib
import json
import random
loginurl = 'https://www.douban.com/accounts/login'
cookie = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie),urllib2.HTTPHandler)
urllib2.install_opener(opener)
cookie=open('cookie').read()
req=urllib2.Request("http://douban.fm/j/mine/playlist?type=s&sid=1519875&pt=175.8&channel=-3")

right_result={}
out=open('starlist.dat','a')
down=open('url.dat','a')
alldata=open('allinfo.dat','a')
while len(right_result)!=85:
    result=urllib2.urlopen(req).read()    
    req.add_header('Cookie', cookie)
    songs=json.loads(result)['song']
    print "got songs list",len(songs)
    for s in songs:
        if s['title']+'-'+s['artist'] not in right_result:
            right_result[s['title']+'-'+s['artist']]=s['url']
            alldata.write(json.dumps(s)+'\n')
            out.write(s['title'].strip().encode('utf-8')+'\t'+s['artist'].strip().encode('utf-8')+'\tp'+s['sid'].strip().encode('utf-8')+'\t'+s['url'].strip().encode('utf-8')+'\n')
            down.write(s['url'].strip().encode('utf-8')+'\n')
            print "add ",s['title'].strip().encode('utf-8')+'\t'+s['artist'].strip().encode('utf-8')+'\t'+s['url'].strip().encode('utf-8')
    #time.sleep(random.randint(1,3))
    out.flush()
    down.flush()
    print "current:",len(right_result)

