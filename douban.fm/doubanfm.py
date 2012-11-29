#coding=utf-8
import os
import re
import urllib, urllib2, cookielib



class douban:
    loginurl = 'https://www.douban.com/accounts/login'
    cookie = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie),urllib2.HTTPHandler)

    params = {
        "form_email":"youremail",
        "form_password":"password",
        "source":"index_nav" #没有的话登录不成功
    }
    def login(self):
        urllib2.install_opener(self.opener)
        response=self.opener.open(self.loginurl, urllib.urlencode(self.params) )
        if response.geturl() == "https://www.douban.com/accounts/login":
            html=response.read()
            imgurl=re.search('<img id="captcha_image" src="(.+?)" alt="captcha" class="captcha_image"/>', html)
            if imgurl:
                url=imgurl.group(1)
                res=urllib.urlretrieve(url, 'v.jpg')
                captcha=re.search('<input type="hidden" name="captcha-id" value="(.+?)"/>' ,html)
                if captcha:
                    vcode=raw_input('请输入图片上的验证码：')
                    self.params["captcha-solution"] = vcode
                    self.params["captcha-id"] = captcha.group(1)
                    self.params["user_login"] = "登录"
                    response=self.opener.open(self.loginurl, urllib.urlencode(self.params))
            print "redirect to : ",response.geturl()
            if response.geturl() == "http://www.douban.com/":
                print 'login success ! '
                c='flag="ok"; ck="7i9w"; dbcl2="49296989:+1YS4W6WUic"; bid="f690ToOm4vU"; __utma=58778424.970383551.1353158320.1353741713.1353755728.11; __utmb=58778424.6.9.1353756937982; __utmc=58778424; __utmz=58778424.1353158320.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
                req=urllib2.Request("http://douban.fm/j/mine/playlist?type=s&sid=1519875&pt=175.8&channel=-3")
                cookie=urllib.urlencode(p)
                req.add_header('Cookie', c)
                result=urllib2.urlopen(req).read()
                #while True:
                    #print self.opener.open("http://douban.fm/j/mine/playlist?type=s&sid=1519875&pt=175.8&channel=-3",urllib.urlencode(self.params)).read()
                    #time.sleep(3)
                return
                print urllib2.urlopen(request).read() 
            else:
                print "error input"
        else:
            print "already login"
            request=urllib2.Request("http://douban.fm/")
            request.add_header("User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
            request.add_header("Accept", "*/*")
            request.add_header("Accept-Charset","UTF-8,*;q=0.5")
            request.add_header("Accept-Encoding", "gzip,deflate,sdch")
            request.add_header("Accept-Language", "en-US,en;q=0.8")
            request.add_header("Connection", "keep-alive")
            request.add_header("Host", "douban.fm")
            request.add_header("Referer", "http://douban.fm/")
            print urllib2.urlopen(request).read()

    
if __name__=="__main__":
    db=douban()
    db.login()
