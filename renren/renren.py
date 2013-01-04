#coding=utf-8
import time
import random
import os
import re
import json
import multiprocessing
import cookielib
import logging
import sys
import urllib
import urllib2

from datetime import datetime
from logging.handlers import RotatingFileHandler
from BeautifulSoup import BeautifulSoup as BS

from encrypt import encrypt_string
# using custom libs
sys.path.append('../')
from alert import alert
from utils import tail

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
    token=None
    file_handler=None                    
    console_handler=None
    formatter=None
    level=None
    username=None
    password=None
    # class constructor , can specify log level eg: debug,info,error,fatal...
    def __init__(self,log_level="debug"):
        self.init_logger(log_level)
        account=open('ACCOUNT').read().strip('\n').split('\t')
        self.username=account[0]
        self.password=account[1]
        self.logger.info("load account file from local :%s",self.username)
    
    def login(self):
        email=self.username
        pwd=self.password
        key = self.get_encrypt_key()
        self.logger.info("get encrypt key: %s" % key)
        data = {
            'email': email,
            'origURL': 'http://www.renren.com/home',
            'icode': '',
            'domain': 'renren.com',
            'key_id': 1,
            'captcha_type': 'web_login',
            'password': encrypt_string(key['e'], key['n'], pwd) if key['isEncrypt'] else pwd,
            'rkey': key['rkey']
        }
        url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
        r = self.open(url, data)
        result = json.loads(r)
        if result['code']:
            print 'login successfully'
            cookie = result['homeUrl'].split('t=')[1].split('&')[0].strip()
            self.set_cookie(cookie)
            r = self.open(result['homeUrl'],login_action=True)
            self.get_token(r)
        else:
            print 'login error', r.text

    def get_token(self, html=''):
        p = re.compile("get_check:'(.*)',get_check_x:'(.*)',env")

        if not html:
            r = self.open('http://www.renren.com')
            html = r

        result = p.search(html)
        self.token = {
            'requestToken': result.group(1),
            '_rtk': result.group(2)
        }
    def get_encrypt_key(self):
        r = self.open('http://login.renren.com/ajax/getEncryptKey')
        return json.loads(r)
    # init logger module
    def init_logger(self,log_level,log_filename="./log/log_renren_module.dat"):
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - <%(filename)s-%(funcName)s:%(lineno)d> : %(message)s')
        self.level=self.LEVELS.get(log_level,logging.NOTSET)
        self.logger = logging.getLogger()
        self.logger.setLevel(self.level)
        self.file_handler = RotatingFileHandler(log_filename,10*1024*1024,10)  # 10M max per file
        self.console_handler = logging.StreamHandler()
        self.file_handler.setFormatter(self.formatter)   
        self.console_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
    
    # set cookie for crawler
    def set_cookie(self,cookie):
        self.cookie['t']=cookie
        self.logger.info("set cookie: %s" % cookie)

    # load cookie from local file
    def load_cookie(self,local_cookie_path="./COOKIE"):
        self.logger.info("load cookie from : %s" % local_cookie_path)
        self.set_cookie(open(local_cookie_path).readline().rstrip('\n'))

    # export current cookie to local file
    def export_cookie(self,local_cookie_path="./COOKIE"):
        export_file=open(local_cookie_path,'w')
        export_file.write(self.cookie['t'])
        self.logger.info("export current cookie")
    
    # input cookie manually (get from chrome),this method will send email and sms to admin.
    def input_cookie(self):
        alert("SCRAWLER-RENREN","Input a New Cookie")
        new_cookie=raw_input("#### input new a cookie ####\n") 
        self.set_cookie(new_cookie)
        self.export_cookie()
    
    # open url using cookie. max-try-times=10
    def open(self,url,params=None,read=True,login_action=False):
        req = urllib2.Request(url)
        cookie=urllib.urlencode(self.cookie)
        req.add_header('Cookie', cookie)
        request=None
        content=None
        if params:
            self.logger.debug("parmas: %s" % params)
            fails = 0
            while True:
                try:
                    if fails >= 10:
                        break
                    self.logger.debug("open: %s #try %s/10#" % (url,fails+1))
                    request = urllib2.urlopen(req,urllib.urlencode(params),timeout=20)
                    if (not login_action) and request.geturl().find("http://www.renren.com/SysHome.do") != -1:
                        self.logger.debug("ATTENTION: cookie expires") 
                        self.input_cookie()
                        cookie=urllib.urlencode(self.cookie)
                        req.add_header('Cookie', cookie)
                        continue
                    if read:
                        content = request.read()
                        return content
                    else:
                        return request
                except:
                    fails += 1
                else:
                    break
        else:
            fails = 0
            while True:
                try:
                    if fails >= 10:
                        break
                    self.logger.debug("open: %s #try %s/10#" % (url,fails+1))
                    request = urllib2.urlopen(req,timeout=20)
                    if (not login_action) and request.geturl().find("http://www.renren.com/SysHome.do") != -1:
                        self.logger.debug("ATTENTION: cookie expires") 
                        self.input_cookie()
                        cookie=urllib.urlencode(self.cookie)
                        req.add_header('Cookie', cookie)
                        continue
                    if read:
                        content = request.read()
                        return content
                    else:
                        return request
                        
                except:
                    fails += 1
                else:
                    break
        self.logger.debug("*** connection timeout ***")
        return None

    def random_walk(self,seed_id="295852491",db="/Users/ericyue/data/renren/random_walk_db"):
        database = open(db).readlines()
        current_pool = set()
        for i in database:
            current_pool.add(i.split('\t')[0])
        self.logger.debug("load pool end,size:%s" % len(current_pool))
        data=self.open("http://www.renren.com/profile.do?id=%s" % seed_id)
        urls=self.get_links_from_page(data)
        ids=set()
        for u in urls:
            ids.union(self.get_ids_from_page(data))
        print ids
        current_pool.union(ids)
        for i in ids:
            profile=self.parse_profile(i)
            uid=profile['uid']
            username=profile['username']
            user_image=profile['user_image']
            print uid,username,user_image
    def get_links_from_page(self,page):
        ids=re.finditer("http://.*renren\.com.*[0-9]{3,14}.*[~\"]",page)
        urls=set()
        for i in ids:
            print i.group()
            urls.add(i.group())
        return urls
    # profile ids on a page
    def get_ids_from_page(self,page):
        ids=re.finditer("http://www.renren.com/profile.do\?.*id=[0-9]{3,13}",page)
        urls=set()
        for i in ids:
            urls.add(i.group())
        return urls
    # get someone's all blogs id (then use get_blog method to get blog content)
    def get_user_blog_ids(self,uid):
        blog_base="http://blog.renren.com/blog/%s/friends?curpage=" % uid
        page=0
        unique_blogs=set() 
        while True:
            self.logger.debug("parse %s" % (blog_base+str(page)))
            data=self.open(blog_base+str(page))
            if not data:
                self.logger.debug("pass")
                continue
            blog_list=re.finditer("http://blog.renren.com/blog/[0-9]{4,12}/[0-9]{5,13}",data)
            try:
                blog_list.next()
            except:   
                break
            for blog in blog_list:
                if blog.group() not in unique_blogs:
                    blog_id=blog.group()
                    print "find a blog:",blog_id
                    unique_blogs.add(blog_id)
            page+=1
        self.logger.debug("got user %s blogs" %uid )
        return unique_blogs
    
    # get blog content by blog url
    def get_blog(self,blog_url):
        bid=blog_url.split('/')[-1]
        data=self.open(str(blog_url))
        if not data:
            return None,None,None
        try:
            title=re.search('<input type="hidden" id="title" name="title" value="(.*)" />',data).groups()[0]
        except:
            return None,None,None
        soup=BS(data)
        content=soup('div',{'id':'blogContent'})[0]
        for tag in content.findAll(True):
            tag.hidden = True
        content.renderContents()
        content_list=[str(i).strip().replace('&hellip;','……').replace('&ldquo;','"').replace('&rdquo;','"').replace('&bull;','•').replace('&mdash;','—').replace('&middot;','·').replace('&nbsp;',' ') for i in content.contents if str(i).strip()!='']
        content='\n'.join(content_list)
        return bid,title,content

    # just leave a footprint on someone's homepage
    def visit(self,uid):
        profile_base="http://www.renren.com/%s/profile?portal=profileFootprint&ref=profile_footprint#pdetails" % uid
        self.logger.debug("visit %s" % uid)
        op=self.open(profile_base,False)
    
    # get someone's friends list by specify uid
    def get_friends_list(self,uid):
        page = 0
        base_url="http://friend.renren.com/GetFriendList.do?id=%s&curpage=" % (uid)
        return_set=[]
        while True:
            url=base_url+str(page)
            data=self.open(url)
            soup=BS(data)
            friend_list=soup('ol',{'id':'friendListCon'})
            friends=friend_list[0]('dl')
            if len(friends) == 0:
                break
            for f in friends:
                name=f('dd')[0]('a')[0].string
                uid=f('dd')[0]('a')[0]['href'].split('id=')[1]
                campus=f('dd')[1].string
                return_set.append((uid,name,campus))
            page+=1
        return return_set
     
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
            data = self.open(status_url)
            if not data:
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
    
    def add_last_update_time_for_status_files(self):
        base="/Users/ericyue/data/renren/renren_friends_status/yuebin/"
        files=os.listdir(base)
        for f in files:
            if f.find('UPDATE')!=-1:
                continue
            try:
                latest=open(base+f).readline().rstrip('\n').split('\t')[1]
            except:
                pass
            j=json.loads(latest)
            o=open(base+f+'_UPDATE','w')
            o.write("%s\t%s" %(j['id'],j['dtime']))
    def get_status(self,output_folder="/Users/ericyue/data/renren/renren_friends_status/yuebin/",uid=None):
        if not uid:
            self.logger.error("uid cannot be None")
            return False
        updated_last=True
        self.logger.debug("get %s status" % uid)
        status_base="http://status.renren.com/GetSomeomeDoingList.do?userId=%s&curpage=" % uid
        status_dict=[]
        try:
            last_update=open(output_folder+uid+'_UPDATE')
        except:
            last_update_str=''    
        else:
            last_update_str=last_update.read()
            last_update.close()
        
        output=open(output_folder+uid,'a')
        
        limit=0
        re_h=re.compile('</?\w+[^>]*>')

        while True:
            status_url=status_base+"%s" % limit
            self.logger.debug("get %s" % status_url)
            data = self.open(status_url)
            if not data:
                continue
            status=json.loads(data)['doingArray']
            if len(status)==0:
                return 
            for s in status:
                s['content']=re_h.sub('',urllib.unquote(s['content']))
                if last_update_str.strip()!='' and float(last_update_str.split('\t')[0])>=float(s['id']):
                    self.logger.debug("DONE!UPDATETIME:%s" % s['dtime'])
                    return
                if s['content'].strip()!='':
                    if updated_last:
                        last_update=open(output_folder+uid+'_UPDATE','w')
                        last_update.write("%s\t%s" %(s['id'],s['dtime']))
                        last_update.close()
                        self.logger.debug("UPDATETIME:%s" % s['dtime'])
                        updated_last=False
                    self.logger.debug(s['content'].strip())
                    line="%s\t%s\n" %(s['id'],json.dumps(s))
                    status_dict.append(line.encode('utf-8'))
            limit+=1
            output.writelines(status_dict)


    def parse_profile(self,url):
        content=self.open(url)
        uid=url.split('id=')[1].strip()
        profile={"uid":uid}
        profile_soup=BS(content)
        try:
            username=profile_soup.title.contents[0].split(' - ')[1].replace('\n','')
        except:
            username=profile_soup('h1',{'class':'username'})[0].contents[0]
        else:
            profile['username']=username
        try:
            user_image=profile_soup('img',{'id':'userpic'})[0]['src'] 
        except Exception,what:
            self.logger.error("error:image %s " % uid)
            return None
        else:
            profile['user_image']=user_image
        
        return profile
    
    def search(self,ofile):
        output=ofile
        search_base_url="http://browse.renren.com/sAjax.do?ajax=1&q=&p=%5B%7B%22prov%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22gend%22%3A%22%E5%A5%B3%E7%94%9F%22%2C%22t%22%3A%22base%22%2C%22city%22%3A%22%E6%B5%B7%E6%B7%80%E5%8C%BA%22%7D%5D&s=0&u=295852491&act=search&offset="
        profile_base_url="http://www.renren.com/%s/profile?portal=profileFootprint&ref=profile_footprint#pdetails"
        begin=random.randint(0,3)
        end=random.randint(100,1000)
        a=0
        for loop in range(begin,end):
            if a>200:
                break
            buffer_lines=[]
            search_url=search_base_url+str(10*loop)
            self.logger.debug("get %s " % search_url) 
            data = self.open(search_url)
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
                try:
                    profile=self.parse_profile(profile_url)
                except:
                    continue
                if profile is None:
                    continue
                else:
                    username=profile['username']
                    user_image=profile['user_image']
                self.logger.debug("%s\t%s" %(uid, username))
                line='%s\t%s\t%s\n'%(uid,username,user_image)
                buffer_lines.append(line.encode('utf-8'))
                time.sleep(random.randint(1,10))
            output.writelines(buffer_lines) 
            output.flush()
        output.close()


