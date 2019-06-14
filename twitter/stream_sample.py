from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

class MyListener(StreamListener):

    def on_data(self, data):
        try:
            with open('data/RandomTweets.json', 'a') as f:
                f.write(data)
                print(data)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        print(status)
        return True

consumer_key = ''
consumer_secret = ''
access_token = '-'
access_secret = ''

if __name__ == '__main__':

    '''
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        twitter_stream = Stream(auth, MyListener())
        twitter_stream.filter(track=['#CAEXIT'])

    '''

    try:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        twitter_stream = Stream(auth, MyListener())
        twitter_stream.sample()

  #      twitter_stream.filter(track=['#CAEXIT'])
    except:
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        twitter_stream = Stream(auth, MyListener())
        twitter_stream.sample()
