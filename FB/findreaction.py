#coding=utf-8

import json
import re
import facebook
import urllib2
import time
import requests
import os
from pprint import pprint
import csv

#Using this

def main():
    #current_page = "113248722127298"
    start=False
    Path = "./data/"
    finished_list = []
    for  root, dirs, fileNames in os.walk(Path+"reaction"):
        finished_list = fileNames
        break

    #graph2 = facebook.GraphAPI(access_token = 'EAAXfzQZBz8EMBAEZCdBTSpMciqzw7xDAP5Ugkqvy85XvCaY62QOfU6vMR11ERlWv8zS9Utvd4cfqX7ypmHDD5ZCYp3YQaZAYqYhRUrxO8A5rJF0HMae3PObZB0LhQ26Nudz2EhNLgzpVXgVoSj5UWgSEBGnrJgAAZD', version = '2.6')
    graph2 = facebook.GraphAPI(access_token = 'EAAEpCePdcvgBAEES9Kl5oQvPeL4S3uHRdCbF3KNdFww5bCk8TphyMTZB1pbj8RupLgYdbdf1voU6uxFLPbTWhPEqhSJv8ZCZCQWrFgZAgk8qQNFnOD6zsby97Mx4cXisoALV0azx0E2cQoxb81rPLsZB5YF4SJr9yyZCe78NsEZCgZDZD', version = '2.9')
    page =  "10155824496656065"

    dirName = 'Tsai'
    Page_dirName = '10155824496656065'
    
    if(os.path.exists(Path+dirName+"/"+Page_dirName+"/after20160226/auto_post_list.txt")):
        with open(Path+dirName+"/"+Page_dirName+"/after20160226/auto_post_list.txt") as post_list_file:
            post_list = post_list_file.readlines()

            csv_exist = os.path.exists(Path+"/reaction_rest2/"+Page_dirName +"_reaction.csv")
            if csv_exist:
                with open(Path+"/reaction_rest2/"+Page_dirName +"_reaction.csv",'r') as post_list_file2:
                    reader = csv.reader(post_list_file2)
                    mylist = list(reader)
                    for line in mylist:
                        if(Page_dirName+"_"+line[0]+"\n" in post_list):
                            post_list.remove(Page_dirName+"_"+line[0]+"\n")

            if(len(post_list)!=0 ):
                if(csv_exist ==False):
                    reaction_csv = open( Path+"/reaction_rest2/"+Page_dirName +"_reaction.csv",'w')
                    reaction_csv.write("PostID,type,name,userID\n")
                else:
                    reaction_csv = open( Path+"/reaction_rest2/"+Page_dirName +"_reaction.csv",'a')

            for post_id in post_list:
                post_id = post_id.strip()

                error_flag3 = 0
                reaction_path = "/" + post_id + "?fields=reactions.limit(1000)"
                try:
                    resp2 = graph2.get_object(reaction_path)

                except facebook.GraphAPIError as g:
                    error_flag3 = 1
                    gstr = "Object with ID"
                    gstr2 = "does not exist"
                    if (gstr in g.message) & (gstr2 in g.message):
                        print g.message,'!!'
                        reaction_csv.write(post_id.split("_")[1]+",null,null,null\n")

                    else:
                        print g.message
                        k = 0
                        while k == 0:
                            time.sleep(0.01)
                            try:
                                resp2 = graph2.get_object(reaction_path)
                                error_flag3 = 0
                                k = k + 1
                            except facebook.GraphAPIError as g2:
                                error_flag3 = 1
                                
                if int(error_flag3) == 0:
                    if('reactions' in resp2):
                        ob = resp2['reactions']
                        result_file_reaction = Path+dirName+"/"+Page_dirName+"/reaction/" + post_id + "_reaction_raw"

                        # with open(result_file_reaction,'w') as outfile3:
                        #     outfile3.write(json.dumps(resp2,ensure_ascii=False).encode('utf8'))
                        name = resp2['reactions']['data']
                        for t in name:
                            try:
                                reaction_csv.write(post_id.split("_")[1]+",")
                                reaction_csv.write(t['type']+"," )
                                reaction_csv.write(t['name'].encode('utf-8')+",")
                                reaction_csv.write(t['id']+"\n")
                            except Exception as e:
                                print(e,"reaction_csv.write error")
                        if len(ob) > 1:
                            if(len(ob['paging']) > 1):
                                n = 1
                                next_page_reaction = ob['paging']['next']
                                get_next_reaction(next_page_reaction,reaction_csv,n,post_id)
                time.sleep(0.001)
    


def get_next_reaction(next_page,reaction_csv,n,post_id):

#def get_next_reaction(next_page,result_file_reaction,n):
    while len(next_page) > 0:
        error_flag7 = 0
        try:
            req = urllib2.Request(next_page)
            content = urllib2.urlopen(req).read()
        except urllib2.HTTPError as e:
            error_flag7 = 1
            print e.message
            i = 0
            while i == 0:
                try:
                    req = urllib2.Request(next_page)
                    content = urllib2.urlopen(req).read()
                    error_flag7 = 0
                    i = i + 1
                except urllib2.HTTPError as e2:
                    print e2,"error\n"
                    time.sleep(0.01)
        if int(error_flag7) == 0:
            next_resu_j_2 = json.loads(content, strict=False)
            #result_reaction = result_file_reaction + "_" + str(n)
            #with open(result_reaction,'w') as outfile:
            #    outfile.write(json.dumps(next_resu_j_2,ensure_ascii=False).encode('utf8'))
            name = next_resu_j_2['data']
            for t in name:
                try:
                    reaction_csv.write(post_id.split("_")[1]+",")
                    reaction_csv.write(t['type']+"," )
                    reaction_csv.write(t['name'].encode('utf-8')+",")
                    reaction_csv.write(t['id']+"\n")
                except Exception as e:
                    print(e,"reaction_csv.write error")
            if(len(next_resu_j_2) > 1):
                if(len(next_resu_j_2['paging']) > 2):
                    n = n + 1
                    next_page = next_resu_j_2['paging']['next']
                    print "\n" + next_page
                else:
                    next_page = ''
            else:
                next_page = ''
        time.sleep(0.001)

if __name__ == "__main__":
    main()
