#!/usr/bin/python

import tweepy
import driver
import binary
import time

# Go to http://dev.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key="eOKlOriKjTtq0WwNMEaNNA"
consumer_secret="YpxnpCH2yiW8DqgxY6VSw7zxeKcv2G9dGxGAQWQ5DTA"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token="94415153-PTcAssFg3EdKaoQCunnS81BS7K1cYIFkLSuW2q8mp"
access_token_secret="0PS2DAFN1ajpPvy5g0Zh5DP6M5gJZ8MCFNqoJr2Z9c"

class StdOutListener(tweepy.StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_status(self, status):
        print status.author.screen_name
        print status.text
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    l = StdOutListener()
    a = tweepy.OAuthHandler(consumer_key, consumer_secret)
    a.set_access_token(access_token, access_token_secret)
    api = tweepy.API(a)

    d = driver.Driver()
    bs = binary.BinaryShifter('Tweet me!')

    while True:
        results = api.search(q='#basketball', rpp=5, result_type='recent')
        bs.update_text(results[0].text)
 
        while bs.shift():       
            bs.update_pattern()
            time.sleep(1)
