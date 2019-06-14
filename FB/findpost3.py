# coding=UTF-8

import json
import re
import facebook
import urllib2
import time
import requests
import os



def main():
    #set  intialize path.date.id_list
    global date_dir
    date_dir = './data/'+'20170416'+ '/'
    until = 'until=2017-04-16'
    since = 'since=2008-01-01'
    skip_id_list = []
    with open("./skip_id_list","r") as infile:
        for line in infile:
            skip_id_list.append(line)

    page_list = []
    with open("./page_list","r") as infile:     #要有一個你要抓的粉絲團的page id list
        for line in infile:
            if((line in skip_id_list )!= True):
                page_list.append(line)
            else:
                print line+"已經抓過了，跳過"
    graph = facebook.GraphAPI(access_token = 'EAAXfzQZBz8EMBAAyvxNoWjYVdplxEE7KvgYZC8aOVMEQwEicWEuLwwUi2MhSKrnnf1KCqVDmcVSveZCZCv08OSbbJLXgZAWX9qDWIeeCNGWcaVBWn6U78ZBTh20gmWpgwjUslgmLDFPYoXpYZCXeeUB6lMwS46dj1EZD', version = '2.5')
    graph2 = facebook.GraphAPI(access_token = 'EAAXfzQZBz8EMBAAyvxNoWjYVdplxEE7KvgYZC8aOVMEQwEicWEuLwwUi2MhSKrnnf1KCqVDmcVSveZCZCv08OSbbJLXgZAWX9qDWIeeCNGWcaVBWn6U78ZBTh20gmWpgwjUslgmLDFPYoXpYZCXeeUB6lMwS46dj1EZD', version = '2.6')

    #traverse every page in page_list
    list_length = len(page_list)
    for i in range(0,list_length,1):
        error_flag = 0
        name_length = len(page_list[i])
        page_id = page_list[i].strip()
        #Post 會抓到的欄位 可以到FB開發者網頁 選擇自己想要的欄位
        #https://developers.facebook.com/docs/graph-api/reference/v2.8/post
        page_path = "/" + page_id + "/posts?fields=id,admin_creator,application,call_to_action,caption,created_time,description,feed_targeting,from,icon,is_hidden,is_published,link,message,name,object_id,parent_id,picture,place,privacy,properties,shares,source,story,story_tags,targeting,to,updated_time,type,with_tags,likes,comments,message_tags,status_type&"+until+"&"+since
        result_dir = page_id

        #If the directory of data(ID)  has not been created, make one
        try:
            os.makedirs(date_dir+result_dir)
        except :
            #   ./data/20170110/ ID/has exised
            print date_dir+result_dir+" has existed"

        try:
            os.makedirs(date_dir+result_dir+"/after20160226")
        except :
            #   ./data/20170110/ ID/has exised
            print date_dir+result_dir+"/after20160226"+" has existed"

        #I want to collect personal fanpage data, so I  only collect the pages with these category.
        writer_category_list = ["Artist","Writer","Public Figure","Author","Musician/Band","Producer","Personal Blog","Comedian","Personal blog","Blogger","Book","Pet"]
        category_error_flag = False
        category =""
        try:
            category = graph.get_object( '/' + page_id + '?fields=category')
            print category['category']
        except:
            category_error_flag = True
            print ("Query page category failed! ID:" +page_id)

        if(category_error_flag != True):
            if((category['category'] in writer_category_list)):
                try:
                    resp = graph.get_object(page_path,limit=30)     #每次拿30篇post 太多會壞掉
                    #print resp
                except facebook.GraphAPIError as g:
                    error_flag = False
                    estr = "Object with ID"
                    estr2 = "does not exist"
                    if (estr in g.message) & (estr2 in g.message):
                        print g.message +"\testr1&2"
                    else:
                        print g.message + "\tnot estr1&2"
                        if "User request limit reached" in g.message:
                            time.sleep(60)
                        loop = True
                        while loop:
                            time.sleep(2)
                            try:
                                resp = graph.get_object (page_path,limit=30)
                                error_flag = True
                                break
                            except facebook.GraphAPIError as g2:
                                if "User request limit reached" in g.message:
                                    print ("User request limit reached so sleep 60s to retry to get resp")
                                    time.sleep(60)

                if (error_flag != True):
                    result_file = date_dir + result_dir + "/auto_post_list"
                    result_file_emotion = date_dir + result_dir + "/after20160226/auto_post_list"

                    #Write auto_post_list.txt
                    ob_length = len(resp['data'])
                    with open(result_file,"w") as outfile , open(result_file_emotion,"w")as  outfile_emotion:
                        for j in range(0,ob_length,1):
                            ob = resp['data'][j]

                             # After 20160226, the post will have emotion reaction
                            # time[0] = year \  time[1] = month \ time[2][0:2] = day
                            emotion_reaction_flag = False
                            ctime = (ob['created_time'].split("-"))
                            if(int(ctime[0])>=2016 and (  ( int(ctime[1])>=3 ) or  ( int(ctime[1])>=2) and int(ctime[2][0:2])>=26) ):
                                emotion_reaction_flag = True

                            #Save to post_list
                            if(outfile.tell() != 0):
                                outfile.write("\n")
                            outfile.write(ob['id'])
                            if(emotion_reaction_flag):
                                if(outfile_emotion.tell() != 0):
                                    outfile_emotion.write("\n")
                                outfile_emotion.write(ob['id'])

                            #save post to PageID_PostID_F_raw
                            result_post = date_dir + result_dir + "/"  + ob['id'] + "_F_raw"
                            with open(result_post,'w') as outfile2:
                                outfile2.write(json.dumps(ob,ensure_ascii=False).encode('utf8'))
                                """
                                if(emotion_reaction_flag):
                                    if(outfile_emotion.tell() != 0):
                                       outfile_emotion.write("\n")
                                    outfile_emotion.write(ob['id'])
                                """
                        if((len(resp) > 1)):
                            if(len(resp['paging']) > 1):
                                next_page = resp['paging']['next']
                                print next_page
                                get_next_post(next_page,result_file,outfile,outfile_emotion,result_dir) #找下一30筆post
                    get_post_comment(result_file,graph)     #找 Post 的 comments


                    reaction_list = ["NONE","LIKE","LOVE","WOW","HAHA","SAD","ANGRY","THANKFUL"]    #找每個reaction有多少人按
                    for l in range(0,len(reaction_list),1):
                        reaction_path = "/" + page_id + "/posts?fields=created_time,reactions.limit(0).type(" + reaction_list[l]  + ").summary(1)&"+until+"&"+since
                        error_flag_1 = False
                        emotion_reaction_flag = False
                        if(emotion_reaction_flag and  l>=2):
                                    pass
                        try:
                            resp2 = graph2.get_object(reaction_path,limit=30)
                        except facebook.GraphAPIError as g:
                            error_flag_1 = True
                            print "error_flag_1 \t"+ g.message
                            loop = True
                            skip =0
                            while loop :
                                time.sleep(2)
                                try:
                                    resp2 = graph2.get_object(reaction_path,limit=30)
                                    error_flag_1 = False
                                    break
                                except facebook.GraphAPIError as g2:
                                    print g2.message+" again"
                                    skip = skip +1
                                    if  skip == 5 :
                                        print "Fail too much time! skip this !"
                                        break
                        if (error_flag_1) == False:
                            ob2_length = len(resp2['data'])
                            for m in range(0,ob2_length,1):

                                ob2 = resp2['data'][m]
                                result_file_reaction_0226 = date_dir + result_dir + "/after20160226/" + ob2['id'] + "_" + reaction_list[l] + "_raw"
                                result_file_reaction = date_dir + result_dir + "/" + ob2['id'] + "_" + reaction_list[l] + "_raw"
                                # After 20160226, the post will have emotion reaction
                                # time[0] = year \  time[1] = month \ time[2][0:2] = day
                                ctime = (ob2['created_time'].split("-"))
                                #if(int(time[0])>=2016 and (  ( int(time[1])>=3 ) or  ( int(time[1])>=2) and int(time[2][0:2])>=26) ):
                                if(int(ctime[0])>=2016 and (  ( int(ctime[1])>=2)) ):
                                    emotion_reaction_flag = True
                                if(l<2):
                                    with open(result_file_reaction,'w') as outfile:
                                        outfile.write(json.dumps(ob2,ensure_ascii=False).encode('utf8'))
                                if(emotion_reaction_flag):
                                        with open(result_file_reaction_0226,'w') as outfile:
                                            outfile.write(json.dumps(ob2,ensure_ascii=False).encode('utf8'))
                            if len(resp2) > 1:
                                if(len(resp2['paging']) > 1):
                                    next_page_reaction = resp2['paging']['next']
                                    get_next_reaction(next_page_reaction,result_dir,reaction_list[l])   #繼續找reaction
                        print "Finish" + reaction_list[l]
                        time.sleep(1)

def get_next_post(next_page,result_file,outfile,outfile_emotion,result_dir):
    while len(next_page) > 0:
        error_flag2 = False
        try:
            req = urllib2.Request(next_page)
            content = urllib2.urlopen(req).read()
        except urllib2.HTTPError as e:
            error_flag2 = True
            print "error_flag2:HTTP ERROR\n"
            loop = True
            while loop:
                try:
                    req = urllib2.Request(next_page)
                    content = urllib2.urlopen(req).read()
                    error_flag2 = False
                    break
                except urllib2.HTTPError as e2:
                    time.sleep(2)
                    print e2+"\terror\n"
        if (error_flag2) != True:
            next_resu = json.loads(content, strict=False)
            ob_length = len(next_resu['data'])
            for i in range(0,ob_length,1):
                ob = next_resu['data'][i]
                print "Post number :" + str(outfile.tell())

                 # After 20160226, the post will have emotion reaction
                # time[0] = year \  time[1] = month \ time[2][0:2] = day
                emotion_reaction_flag = False
                ctime = (ob['created_time'].split("-"))
                if(int(ctime[0])>=2016 and (  ( int(ctime[1])>=3 ) or  ( int(ctime[1])>=2) and int(ctime[2][0:2])>=26) ):
                    emotion_reaction_flag = True

                #Save to post_list
                if(outfile.tell() != 0):
                    outfile.write("\n")
                outfile.write(ob['id'])

                if(emotion_reaction_flag):
                    if(outfile_emotion.tell() != 0):
                        outfile_emotion.write("\n")
                    outfile_emotion.write(ob['id'])

                result_post = date_dir + result_dir + "/"  + ob['id'] + "_F_raw"
                with open(result_post,'w') as outfile2:
                    outfile2.write(json.dumps(ob,ensure_ascii=False).encode('utf8'))
            if((len(next_resu) > 1)):
                print "in"
                if(len(next_resu['paging']) > 1):
                    next_page = next_resu['paging']['next']
                    print "\n" + next_page
                else:
                    next_page = ''
            else:
                next_page = ''
        time.sleep(1)

def get_post_comment(result_file,graph):

    post_list = []
    with open(result_file,"r") as infile:
        for line in infile:
            post_list.append(line)
    list_length = len(post_list)
    for i in range(0,list_length,1):
        time.sleep(1)
        error_flag3 = 0
        name_length = len(post_list[i])
        post_id = post_list[i].strip()
        print post_id
        #comment 會抓到的東西 可以到FB開發者網頁 找自己要的欄位名稱
        comment_path = "/" + post_id + "/comments" + "?fields=from,message,message_tags,created_time,id,comments.limit(50){from,id,message,message_tags,created_time,like_count,parent,can_remove,user_likes},comment_count,user_likes,can_remove,parent,like_count"
        result_dir = post_id.split("_")[0]
        result_comment = date_dir + result_dir + "/"  + post_id + "_raw"
        try:
            resp_2 = graph.get_object(comment_path,limit=300)   #每次300個 可能會壞掉
        except facebook.GraphAPIError as g:
            error_flag3 = 1
            gstr = "Object with ID"
            gstr2 = "does not exist"
            if (gstr in g.message) & (gstr2 in g.message):
                print g.message
            else:
                print g.message
                if "User request limit reached" in g.message:
                    time.sleep(60)
                k = 0
                while k == 0:
                    time.sleep(5)
                    try:
                        resp_2 = graph.get_object(comment_path,limit=10)    #自動減量 可自訂
                        error_flag3 = 0
                        k = k + 1
                    except facebook.GraphAPIError as g2:
                        if "User request limit reached" in g.message:
                            time.sleep(60)
        except requests.exceptions.ConnectionError as r:
            error_flag3 = 1
            print r.message
            k2 = 0
            while k2 == 0:
                try:
                    resp_2 = graph.get_object(comment_path,limit=100)
                    error_flag3 = 0
                    k2 = k2 + 1
                except requests.exceptions.ConnectionError as r2:
                    time.sleep(60)
        if int(error_flag3) == 0:
            with open(result_comment, 'w') as outfile2:
                outfile2.write(json.dumps(resp_2,ensure_ascii=False).encode('utf8'))
            ob = resp_2['data']
            ob_len = len(ob)
            for j in range(0,ob_len,1):
                resu_id = ob[j]['id']
                resu_comcom = ob[j]['comment_count']
                if int(resu_comcom) > 50:
                    next_ob_page = ob[j]['comments']
                    if len(next_ob_page['paging']) > 1:
                        next_comcom_page = next_ob_page['paging']['next']
                        get_com_com(next_comcom_page,resu_id,result_dir,post_id)    #找subcomment
            print "Get F and Comment_1 Ok\n"
            if(len(resp_2) > 1):
                if(len(resp_2['paging']) > 1):
                    n = 1
                    next_page = resp_2['paging']['next']
                    get_next_comment(next_page,result_dir,post_id,n,graph)  #找下N筆comment

def get_next_comment(next_page,result_dir,post_id,n,graph):
    while len(next_page) > 0:
        error_flag4 = 0
        try:
            req = urllib2.Request(next_page)
            content = urllib2.urlopen(req).read()
        except urllib2.HTTPError as e:
            error_flag4 = 1
            print e.message
            #i = 0
            #while i == 0:
            try:
                req = urllib2.Request(next_page)
                content = urllib2.urlopen(req).read()
                error_flag4 = 0
                #i = i + 1
            except urllib2.HTTPError as e2:
                print e2
                print post_id + " error\n"

        if int(error_flag4) == 0:
            next_resu_j_2 = json.loads(content, strict=False)
            next_ob = next_resu_j_2['data']
            result_comment = date_dir + result_dir + "/" + post_id + "_raw_" + str(n)   #日期要跟著改
            with open(result_comment,'w') as outfile:
                outfile.write(json.dumps(next_resu_j_2,ensure_ascii=False).encode('utf8'))
            for i in range(0,len(next_ob),1):
                resu_id = next_ob[i]['id']
                resu_comcom = next_ob[i]['comment_count']
                if int(resu_comcom) > 50:
                    next_ob_page = next_ob[i]['comments']
                    if len(next_ob_page['paging']) > 1:
                        next_comcom_page = next_ob_page['paging']['next']
                        get_com_com(next_comcom_page,resu_id,result_dir,post_id)    #找subcomment
            n = n + 1
            print "Get Comment_next Ok\n"
            if(len(next_resu_j_2) > 1):
                if(len(next_resu_j_2['paging']) > 2):
                    next_page = next_resu_j_2['paging']['next']
                else:
                    next_page = ''
            else:
                next_page = ''

def get_com_com(next_page,com_id,result_dir,post_id):
    error_flag5 = 0
    try:
        req = urllib2.Request(next_page)
        content = urllib2.urlopen(req).read()
    except urllib2.HTTPError as e:
        error_flag5 = 1
        print e.message
        k = 0
        while k == 0:
            time.sleep(5)
            try:
                req = urllib2.Request(next_page)
                content = urllib2.urlopen(req).read()
                error_flag5 = 0
                k = k + 1
            except urllib2.HTTPError as e2:
                print e2.message
    except requests.exceptions.ConnectionError as r:
        error_flag5 = 1
        print r.message
        k2 = 0
        while k2 == 0:
            time.sleep(5)
            try:
                req = urllib2.Request(next_page)
                content = urllib2.urlopen(req).read()
                error_flag5 = 0
                k2 = k2 + 1
            except requests.exceptions.ConnectionError as r2:
                print r2.message
                time.sleep(60)
    if int(error_flag5) == 0:
        next_comcom = json.loads(content, strict=False)
        result_comcom = date_dir + result_dir + "/" + post_id + "_" + com_id +"_raw"    #日期要跟著改
        with open(result_comcom, 'w') as outfile:
            outfile.write(json.dumps(next_comcom,ensure_ascii=False).encode('utf8'))
        if(len(next_comcom) > 1):
            if(len(next_comcom['paging']) > 2):
                n = 1
                next_page = next_comcom['paging']['next']
                get_next_comcom(next_page,result_dir,post_id,com_id,n)  #找下N筆subcomment

def get_next_comcom(next_page,result_dir,post_id,com_id,n):
    error_flag6 = 0
    try:
        req = urllib2.Request(next_page)
        content = urllib2.urlopen(req).read()
    except urllib2.HTTPError as e:
        error_flag6 = 1
        print e.message
        i = 0
        while i == 0:
            time.sleep(5)
            try:
                req = urllib2.Request(next_page)
                content = urllib2.urlopen(req).read()
                error_flag6 = 0
                i = i + 1
            except urllib2.HTTPError as e2:
                print post_id + " error\n"
    except requests.exceptions.ConnectionError as r:
        error_flag6 = 1
        print r.message
        k2 = 0
        while k2 == 0:
            time.sleep(2)
            try:
                req = urllib2.Request(next_page)
                content = urllib2.urlopen(req).read()
                error_flag6 = 0
                k2 = k2 + 1
            except requests.exceptions.ConnectionError as r2:
                time.sleep(60)
    if int(error_flag6) == 0:
        next_comcom = json.loads(content, strict=False)
        result_comcom = date_dir + result_dir + "/" + post_id + "_" + com_id  +"_raw_" + str(n) #日期要跟著改
        with open(result_comcom,'w') as outfile:
            outfile.write(json.dumps(next_comcom,ensure_ascii=False).encode('utf8'))
        if(len(next_comcom) > 1):
            if(len(next_comcom['paging']) > 2):
                n =  n + 1
                next_page = next_comcom['paging']['next']
                get_next_comcom(next_page,result_dir,post_id,com_id,n)  #recursive

def get_next_reaction(next_page,result_dir,reaction_type):
    while len(next_page) > 0:
        error_flag7 = False
        try:
            req = urllib2.Request(next_page)
            content = urllib2.urlopen(req).read()
        except urllib2.HTTPError as e:
            error_flag7 = True
            print "error_flag7  "+e.message
            loop = True
            while loop:
                try:
                    req = urllib2.Request(next_page)
                    content = urllib2.urlopen(req).read()
                    error_flag7 = False
                    break
                except urllib2.HTTPError as e2:
                    print "error e2:"+e2+"\n"
                    time.sleep(2)

        if (error_flag7) == False:
            next_resu_j_2 = json.loads(content, strict=False)
            ob_length = len(next_resu_j_2['data'])
            emotion_reaction_flag = False
            for j in range(0,ob_length,1):
                #
                if(emotion_reaction_flag and not(reaction_type == "NONE" or reaction_type == "LIKE"  )):
                    pass
                ob = next_resu_j_2['data'][j]
                # After 20160226, the post will have emotion reaction
                # time[0] = year \  time[1] = month \ time[2][0:2] = day
                #print "emotion_reaction_flag:\t"+emotion_reaction_flag
                ctime = (ob['created_time'].split("-"))
                #if(int(time[0])>=2016 and (  ( int(time[1])>=3 ) or  ( int(time[1])>=2) and int(time[2][0:2])>=26) ):
                if(int(ctime[0])>=2016 and (  ( int(ctime[1])>=2)) ):
                    emotion_reaction_flag = True
                #
                result_reaction_0226 = date_dir + result_dir + "/after20160226/" + ob['id'] + "_" + reaction_type + "_raw"

                result_reaction = date_dir + result_dir + "/" + ob['id'] + "_" + reaction_type + "_raw"

                #


                if(reaction_type == "NONE" or reaction_type == "LIKE"  ):
                    with open(result_reaction,'w') as outfile:
                        outfile.write(json.dumps(ob,ensure_ascii=False).encode('utf8'))
                if(emotion_reaction_flag) :
                    with open(result_reaction_0226,'w') as outfile:
                        outfile.write(json.dumps(ob,ensure_ascii=False).encode('utf8'))
                        #print json.dumps(ob,ensure_ascii=False).encode('utf8')

            if(len(next_resu_j_2) > 1):
                if(len(next_resu_j_2['paging']) > 1):
                    next_page = next_resu_j_2['paging']['next']
                    print "\n" + next_page
                else:
                    next_page = ''
            else:
                next_page = ''
        time.sleep(1)

if __name__ == "__main__":
    main()
