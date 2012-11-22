#encoding=utf-8
import urllib2
import time
import random
import re
import json
import multiprocessing
import urllib
import cookielib
from bs4 import BeautifulSoup as BS

class Renren:
  login_page = "http://www.renren.com/PLogin.do"
  opener = None

  def login(self,user,password):
    try:
      cj = cookielib.CookieJar()
      self.opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      chrome="Mozilla/5.1 (Macintosh; Intel Mac OS X 10_7_1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
      self.opener.addheaders = [('User-agent',chrome)]
      data = urllib.urlencode({"email":user,"password":password})
      self.opener.open(self.login_page,data)
      print "Login Successfully!"
    except Exception,e:
      raise Exception(e)

  def get_blog(self,uid):
    blog_base="http://blog.renren.com/blog/%s/friends?curpage=" % uid
    limit=0
    output=open('./renren_blogs/%s'+uid,'a')
    while True:
      print blog_base+str(limit)
      op=self.opener.open(blog_base+str(limit))
      data=op.read()
      unique_blogs=set()
      blog_list=re.finditer("http://blog.renren.com/blog/[0-9]{4,12}/[0-9]{5,13}",data)
      for blog in blog_list:
        unique_blogs.add(blog.group())
      print unique_blogs
      if len(unique_blogs)==0:
        return
      limit+=1

  def visit(self,uid):
    profile_base="http://www.renren.com/%s/profile?portal=profileFootprint&ref=profile_footprint#pdetails" % uid
    try:
      op=self.opener.open(profile_base)
    except:
      print "error"
      return
    data=op.read()
    print data
  def get_my_friends_list(self): 
    friend_list_url="http://friend.renren.com/myfriendlistx.do"
    mylist=[]
    op = self.opener.open(friend_list_url)
    data=op.read()
    data=re.search('friends=\[{.*?}\];',data)
    data=data.group()
    data=data[8:-1]
    data=data.replace('tr','Tr').replace('false','False')
    friends=eval(data)
    for f in friends:
      mylist.append((f['id'],f['name'].encode('utf-8')))
    if len(mylist)!=0:
      return mylist
    else:
      return None

  def get_new_status(self,today):
    status_all_base="http://status.renren.com/GetFriendDoing.do?curpage="
    status_dict=[]
    output=open('renren_new_status','a')
    limit=0
    re_h=re.compile('</?\w+[^>]*>')

    while True:
      status_url=status_all_base+"%s" % limit
      print status_url
      op = self.opener.open(status_url)
      try:
        data=op.read()
      except:
        continue
      print data
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
 

  def get_status(self,ofile,uid=None):
    status_base="http://status.renren.com/GetSomeomeDoingList.do?userId=%s&curpage=" % uid
    status_dict=[]
    output=ofile#open('renren_friends_status','a')
    limit=0
    re_h=re.compile('</?\w+[^>]*>')

    while True:
      status_url=status_base+"%s" % limit
      print status_url
      op = self.opener.open(status_url)
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
          print s['content']
          line="%s\t%s\n" %(s['id'],json.dumps(s))
          #line="%s\t%s\t%s\t%s\n"%(s['id'],s['userId'],s['dtime'],s['content'])
          status_dict.append(line.encode('utf-8'))
      limit+=1
      output.writelines(status_dict)
    #output.flush()

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
      print "processing - ",search_url
      op = self.opener.open(search_url)
      print "read ok"
      data = op.read()
      user_ids=set()
      soup=BS(data)
      print "parse html ok",len(data)
      result=soup('a')
      
      print "search for user_ids"
      for i in result:
        if i['href'].find('&id=')!=-1:
          user_ids.add(i['href'].split('id=')[1].split('&')[0])
      print "got all ids on page"
      print user_ids
      for uid in user_ids:
        a+=1
        profile_url=profile_base_url % uid
        op = self.opener.open(profile_url)
        content=op.read()
        profile_soup=BS(content)
        try:
          username=profile_soup.title.contents[0].split(' - ')[1].replace('\n','')
        except:
          username=profile_soup('h1',{'class':'username'})[0].contents[0]
        try:
          user_image=profile_soup('img',{'id':'userpic'})[0]['src'] 
        except Exception,what:
          print "error:image",uid
          print profile_soup('img',{'id':'userpic'})
          continue
        line='%s\t%s\t%s\n'%(uid,username,user_image)
        buffer_lines.append(line.encode('utf-8'))
        print uid#,username,user_image
        time.sleep(random.randint(1,10))
      print buffer_lines
      output.writelines(buffer_lines) 
      output.flush()
    output.close()


