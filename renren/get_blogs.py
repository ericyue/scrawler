#coding=utf-8
from renren import Renren
import time
import random
from datetime import datetime
import json
import os
if __name__=="__main__":
    renren=Renren()
    renren.load_cookie()
    flist=renren.get_friends_list('295852491')
    for f in flist:
        output_path="/Users/ericyue/data/renren/renren_blogs/%s" % f[0]
        if os.path.exists(output_path):
           print "already save"
           continue 
        output=open(output_path,'a')
        blogs=renren.get_user_blog_ids(f[0])
        for url in blogs:
            bid,title,content=renren.get_blog(url)
            if bid and title and content:
                jsonstr={"bid":bid,"title":title,"content":content}
                output.write("%s\n" % (json.dumps(jsonstr)) )
                output.flush()
        time.sleep(random.randint(1,10))
    
