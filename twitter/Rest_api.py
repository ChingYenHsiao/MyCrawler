#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs
import urllib
import os
import json
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

CONSUMER_KEY = "X"
CONSUMER_SECRET = "X"

OAUTH_TOKEN = "X-X"
OAUTH_TOKEN_SECRET = "X"



#Write data to txt file
def write_to_raw(post_id, content):   

    raw_path = os.path.join(post_id + ".txt")
    #print ("Finished File :"+str(post_id))
    try:
        # http://stackoverflow.com/questions/5483423/how-to-write-unicode-strings-into-a-file
        # It claims that with open will  surely close file 
        with open(raw_path, 'wb') as out:
            out.write(content.encode('utf-8'))
            
       # raw_file = open(raw_path, 'wb')    
      #  raw_file.write(content.encode('utf-8'))
        
    except:
        print ("Warning:"+post_id+" write to raw failed")
    #raw_file.close()


def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

if __name__ == "__main__":
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        #r = requests.get(url="https://api.twitter.com/1.1/statuses/mentions_timeline.json", auth=oauth)
        r = requests.get(url="https://api.twitter.com/1.1/search/tweets.json?q=%23開心"+"&lang=zh&until=2016-06-22", auth=oauth)
       # s=''+str(r.json())
        #print s
        #print urllib.unquote(s).decode("utf-8")
        #print json.dumps(r.json(), ensure_ascii=False) 
       # print  s.decode('cp950').encode('utf-8')
        write_to_raw("result",json.dumps(r.json(), ensure_ascii=False) )