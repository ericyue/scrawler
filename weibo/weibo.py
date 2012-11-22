#! /usr/bin/env python
#coding=utf8
import urllib
import urllib2
import cookielib
import base64
import re
import os
import json
import hashlib
from BeautifulSoup import BeautifulSoup as BS

class Weibo:
  uid= None
  cj = None
  cookie_support = None
  opener = None
  postdata = {
      'entry': 'weibo',
      'gateway': '1',
      'from': '',
      'savestate': '7',
      'userticket': '1',
      'ssosimplelogin': '1',
      'vsnf': '1',
      'vsnval': '',
      'su': '',
      'service': 'miniblog',
      'servertime': '',
      'nonce': '',
      'pwencode': 'wsse',
      'sp': '',
      'encoding': 'UTF-8',
      'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
      'returntype': 'META'
  }

  def get_servertime(self):
      url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&client=ssologin.js(v1.3.18)&_=1329806375939'
      data = urllib2.urlopen(url).read()
      p = re.compile('\((.*)\)')
      try:
          json_data = p.search(data).group(1)
          data = json.loads(json_data)
          servertime = str(data['servertime'])
          nonce = data['nonce']
          return servertime, nonce
      except:
          print 'Get severtime error!'
          return None

  def get_pwd(self,pwd, servertime, nonce):
      pwd1 = hashlib.sha1(pwd).hexdigest()
      pwd2 = hashlib.sha1(pwd1).hexdigest()
      pwd3_ = pwd2 + servertime + nonce
      pwd3 = hashlib.sha1(pwd3_).hexdigest()
      return pwd3

  def get_user(self,username):
      username_ = urllib.quote(username)
      username = base64.encodestring(username_)[:-1]
      return username

  def get_uid(self):
    if self.uid == None:
      url="http://weibo.com/"
      url_content=urllib2.urlopen(url).read()
      uid=url_content.split("$CONFIG['uid'] = '")[1].split("'")[0]
      print "got uid:",uid
      self.uid=uid

  def login(self,username,pwd):
      #check if the cookies file exists
      if os.path.isfile('cookies_weibo_'+username):
        self.cj=cookielib.LWPCookieJar()
        self.cj.load('cookies_weibo_'+username)
        self.cookie_support = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)  
        url="http://weibo.com/"
        url_content=urllib2.urlopen(url).read()
        try:
          p = re.compile('location\.replace\(\"(.*?)\"\)')
          login_url = p.search(url_content).group(1)
        except:
          p = re.compile('location\.replace\(\'(.*?)\'\)')
          login_url = p.search(url_content).group(1)
        try:
            urllib2.urlopen(login_url)
            print "login successfully!"
        except Exception,what:
            print 'login error!',what
   
        print "load cookies from file"
        self.get_uid()
        return
      
      url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
      self.cj=cookielib.LWPCookieJar()
      self.cookie_support = urllib2.HTTPCookieProcessor(self.cj)
      self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)
      urllib2.install_opener(self.opener)
      
      try:
          servertime, nonce = self.get_servertime()
      except:
          return
      self.postdata['servertime'] = servertime
      self.postdata['nonce'] = nonce
      self.postdata['su'] = self.get_user(username)
      self.postdata['sp'] = self.get_pwd(pwd, servertime, nonce)
      self.postdata = urllib.urlencode(self.postdata)
      headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
      req  = urllib2.Request(
          url = url,
          data = self.postdata,
          headers = headers
      )
      result = urllib2.urlopen(req)
      text = result.read()
      try:
        p = re.compile('location\.replace\(\"(.*?)\"\)')
        login_url = p.search(text).group(1)
      except:
        p = re.compile('location\.replace\(\'(.*?)\'\)')
        login_url = p.search(text).group(1)
      try:
          urllib2.urlopen(login_url)
          print "login successfully!"
          self.cj.save('cookies_weibo_'+username)
          print "save cookies to file"
      except Exception,what:
          print 'login error!',what
  
  def follow_list(self,main_uid=None):
    if main_uid==None:
      main_uid=self.uid
    follow_dict={}
    limit=1
    while True:
      url="http://weibo.com/%s/follow?page=%s" % (main_uid,limit)
      print "parsing url ======> ",url
      content=urllib2.urlopen(url).read()
      html_content=re.search(r"STK && STK.pageletM && STK.pageletM.view.*\((.*pl_relation_hisFollow\",\"js\":.*,\"html\":\".*<!--小分页-->\"})\)",content).groups()
      html_content=html_content[0]
      html_content=json.loads(html_content)
      soup=BS(html_content['html'])
      tmp=soup('img',{'width':'50'})
      for i in tmp:
        nickname=i['alt']
        uid=i['usercard'].split('=')[1]
        image=i['src']
        print "%s\t%s\t%s" %(uid,nickname,image)
        if uid in follow_dict:
          print len(follow_dict)," follow"
          return
        else:
          follow_dict[uid]={"nickname":nickname,"image":image}
      limit+=1
  
  
  def search_user(self,keywords):
    search_user_base_url="http://s.weibo.com/user/%s&Refer=weibo_user" % keywords
    print search_user_base_url
    content=urllib2.urlopen(search_user_base_url).read()
    html_content=re.search(r"STK && STK.pageletM && STK.pageletM.view.*\((.*pl_user_feedList\",\"js\":.*,\"html\":\".*\"})\)",content).groups()
    html_content=html_content[0]
    html_content=json.loads(html_content)
    print html_content['html']
    soup=BS(html_content['html'])
    tmp=soup('div',{'class':'list_person clearfix'})
    for i in tmp:
      print "============",i
      continue
      nickname=i['alt']
      uid=i['usercard'].split('=')[1]
      image=i['src']
      print "%s\t%s\t%s" %(uid,nickname,image)
      if uid in follow_dict:
        print len(follow_dict)," follow"
        return
      else:
        follow_dict[uid]={"nickname":nickname,"image":image}
 
  def search_weibo(self,keywords):
    search_user_base_url="http://s.weibo.com/weibo/%s&Refer=user_weibo" % keywords

