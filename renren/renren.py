#coding=utf-8
import urllib2
import time
import random
from datetime import datetime
import re
import json
import multiprocessing
import urllib
from logging.handlers import RotatingFileHandler
import cookielib
from BeautifulSoup import BeautifulSoup as BS
import logging

class Renren:
    LEVELS={'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL}
    cookie={"t":""}
    opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar())) 
    urllib2.install_opener(opener)
    logger=None
    file_handler=None                    
    console_handler=None
    formatter=None
    level=None
    def __init__(self,log_level="debug"):
        self.init_logger(log_level)        
   
    def init_logger(self,log_level):
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - <%(filename)s-%(funcName)s:%(lineno)d> : %(message)s')
        LOG_FILENAME="./log/log_renren_module.dat"
        self.level=self.LEVELS.get(log_level,logging.NOTSET)
        self.logger = logging.getLogger()
        self.logger.setLevel(self.level)
        self.file_handler = RotatingFileHandler(LOG_FILENAME,10*1024*1024,10)
        self.console_handler = logging.StreamHandler()
        self.file_handler.setFormatter(self.formatter)   
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
    
    def set_cookie(self,cookie):
        self.cookie['t']=cookie
        self.logger.info("set new cookie: %s" % cookie)
        
    def input_cookie(self,cookie):
        new_cookie=raw_input("input new a cookie:") 
        self.set_cookie(new_cookie)

    def open(self,url,params=None):
        req = urllib2.Request(url)
        cookie=urllib.urlencode(self.cookie)
        req.add_header('Cookie', cookie)
        if params:
            self.logger.debug("parmas: %s" % params)
            self.logger.debug("open: %s" % url)
            request = urllib2.urlopen(req,urllib.urlencode(params))
        else:
            self.logger.debug("open: %s" % url)
            request = urllib2.urlopen(req)
        return request
         
    def get_user_blog_ids(self,uid):
        blog_base="http://blog.renren.com/blog/%s/friends?curpage=" % uid
        page=0
        unique_blogs=set() 
        while True:
            self.logger.debug("parse %s" % (blog_base+str(page)))
            op=self.open(blog_base+str(page))
            data=op.read()
            blog_list=re.finditer("http://blog.renren.com/blog/[0-9]{4,12}/[0-9]{5,13}",data)
            if len(blog_list)==0:
                break
            for blog in blog_list:
                if blog.group not in unique_blogs:
                    print "find a blog:",blog.group()
                unique_blogs.add(blog.group())
            page+=1
        self.logger.debug("got user ",uid," blogs")

    def get_blog(self,blog_url):
        pass

    def visit(self,uid):
        profile_base="http://www.renren.com/%s/profile?portal=profileFootprint&ref=profile_footprint#pdetails" % uid
        self.logger.debug("visit %s" % uid)
        op=self.open(profile_base)
     
    def get_my_friends_list(self): 
        self.logger.debug("get my friends'id list begin")
        friend_list_url="http://friend.renren.com/myfriendlistx.do"
        mylist=[]
        op = self.open(friend_list_url)
        data=op.read()
        data=re.search('friends=\[{.*?}\];',data)
        data=data.group()
        data=data[8:-1]
        data=data.replace('tr','Tr').replace('false','False')
        friends=eval(data)
        for f in friends:
            self.logger.debug("add friend id : %s" % f['id'])
            mylist.append((f['id'],f['name'].encode('utf-8')))
        self.logger.debug("get my friends's id end")
        if len(mylist)!=0:
            return mylist
        else:
            return None

    def get_new_status(self,today):
        self.logger.debug("get new status begin")
        status_all_base="http://status.renren.com/GetFriendDoing.do?curpage="
        status_dict=[]
        output=open('./data/renren_new_status','a')
        limit=0
        re_h=re.compile('</?\w+[^>]*>')

        while True:
            status_url=status_all_base+"%s" % limit
            print status_url
            op = self.open(status_url)
            try:
                data=op.read()
            except:
                continue
            status=json.loads(data)['doingArray']
            if len(status)==0:
                return 
            for s in status:
                if s['dtime'].split(' ')[0]!=today:
                    return
                s['content']=re_h.sub('',urllib.unquote(s['content']))
                if s['content'].strip()!='':
                    line="%s\t%s\n" %(s['id'],json.dumps(s))
                    status_dict.append(line.encode('utf-8'))
            limit+=1
            output.writelines(status_dict)
 
        self.logger.debug("get new status end")

    def get_status(self,ofile,uid=None):
        if not uid:
            self.logger.error("uid cannot be None")
            return False
        self.logger.debug("get %s status" % uid)
        status_base="http://status.renren.com/GetSomeomeDoingList.do?userId=%s&curpage=" % uid
        status_dict=[]
        output=ofile
        limit=0
        re_h=re.compile('</?\w+[^>]*>')

        while True:
            status_url=status_base+"%s" % limit
            self.logger.debug("get %s" % status_url)
            op = self.open(status_url)
            try:
                data=op.read()
            except:
                continue
            status=json.loads(data)['doingArray']
            if len(status)==0:
                return 
            for s in status:
                s['content']=re_h.sub('',urllib.unquote(s['content']))
                if s['content'].strip()!='':
                    self.logger.debug(s['content'].strip())
                    line="%s\t%s\n" %(s['id'],json.dumps(s))
                    status_dict.append(line.encode('utf-8'))
            limit+=1
            output.writelines(status_dict)

    def search(self,ofile):
        output=ofile
        search_base_url="http://browse.renren.com/sAjax.do?ajax=1&q=&p=%5B%7B%22prov%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22gend%22%3A%22%E5%A5%B3%E7%94%9F%22%2C%22t%22%3A%22base%22%2C%22city%22%3A%22%E6%B5%B7%E6%B7%80%E5%8C%BA%22%7D%5D&s=0&u=295852491&act=search&offset="
        profile_base_url="http://www.renren.com/%s/profile?portal=profileFootprint&ref=profile_footprint#pdetails"
        begin=random.randint(0,50)
        end=random.randint(51,1000)
        a=0
        for loop in range(begin,end):
            if a>200:
                break
            buffer_lines=[]
            search_url=search_base_url+str(10*loop)
            self.logger.debug("get" % search_url) 
            op = self.open(search_url)
            self.logger.debug("got page")
            data = op.read()
            user_ids=set()
            soup=BS(data)
            result=soup('a')
            for i in result:
                if i['href'].find('&id=')!=-1:
                    user_ids.add(i['href'].split('id=')[1].split('&')[0])
            self.logger.debug("got all ids on page")
            for uid in user_ids:
                a+=1
                profile_url=profile_base_url % uid
                op = self.open(profile_url)
                content=op.read()
                profile_soup=BS(content)
                try:
                    username=profile_soup.title.contents[0].split(' - ')[1].replace('\n','')
                except:
                    username=profile_soup('h1',{'class':'username'})[0].contents[0]
                try:
                    user_image=profile_soup('img',{'id':'userpic'})[0]['src'] 
                except Exception,what:
                    self.logger.error("error:image %s " % uid) 
                    continue
                line='%s\t%s\t%s\n'%(uid,username,user_image)
                buffer_lines.append(line.encode('utf-8'))
                time.sleep(random.randint(1,10))
            output.writelines(buffer_lines) 
            output.flush()
        output.close()


