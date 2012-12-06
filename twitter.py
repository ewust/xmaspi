#!/usr/bin/python

import tweepy
import driver
import binary
import time
import sys
import rgb_strand
import webcolors
from api_keys import *

NUM_BULBS = 100

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


MAX_MENTION_FILE='max_mention_id'
def get_last_max_id():
    f = open(MAX_MENTION_FILE, 'r')
    mid = int(f.readline().strip())
    f.close()
    return mid

def put_last_max_id(mid):
    f = open(MAX_MENTION_FILE, 'w')
    f.write(str(mid)+'\n')
    f.close()

def handle_ip():

    d = driver.Driver()
    bs = binary.BinaryShifter()


def handle_rainbow():
    colors = [(15, 0, 0), \
            (15, 3, 0), \
            (15, 15, 0), \
            (0,   15,   0), \
            (0,   0, 15), \
            (4,  14, 13), \
            (14, 0, 14) ]


    strand = rgb_strand.RGBStrand(NUM_BULBS)
    strand.set_strand_pattern(colors)
    strand.set_strand_brightness(200)

    for i in range(200):
        idx = i % len(colors)
        strand.push_top(200, colors[idx][0], colors[idx][1], colors[idx][2])


def handle_binary(text):
    
    d = driver.Driver()
    bs = binary.BinaryShifter(text)

def handle_color(color):
    
    strand = rgb_strand.RGBStrand(NUM_BULBS)
    try:
        rgb = webcolors.name_to_rgb(color)
        strand.set_strand_color(rgb[0]/16, rgb[1]/16, rgb[2]/16)
        time.sleep(10)
        # respond to user?
    except:
        # Shame user?
        pass



def handle_new_mention(mention):

    tweet = str(mention.text).strip()
    sys.stdout.write('%s: \'%s\': ' % (mention.user.screen_name, tweet))
    if tweet.lower().startswith('@bbb_blinken '):
        cmd = tweet[len('@bbb_blinken '):]

        if cmd.lower().startswith('ip'):
            sys.stdout.write('ip\n')
            handle_ip()

        elif cmd.lower().startswith('all '):
            color = cmd[len('all '):].lower()
            sys.stdout.write('color(%s)\n' % color)
            handle_color(color)

        elif cmd.lower().startswith('rainbow'):
            sys.stdout.write('running rainbow\n')
            handle_rainbow()
            
        
        elif cmd.lower().startswith('binary '):
            arg = cmd[len('binary '):]
            sys.stdout.write('binary(%s)\n' % arg)
            handle_binary(arg)
        else:
            sys.stdout.write('\n')
            return 0
    else:
        sys.stdout.write('\n')
        return 0
    return 1
        


def func(lock):

    #l = StdOutListener()
    a = tweepy.OAuthHandler(consumer_key, consumer_secret)
    a.set_access_token(access_token, access_token_secret)
    api = tweepy.API(a)

    max_id = get_last_max_id()

    while True:
        lock.acquire()
        round_max_id = max_id
        num_mentions_run = 0
        mentions = api.mentions()

        for mention in mentions:
            if mention.id > max_id:
                print 'tweet %d > %d' % (mention.id, max_id)
                num_mentions_run + handle_new_mention(mention)
                if mention.id > round_max_id:
                    round_max_id = mention.id
                if num_mentions_run > 0:
                    # given someone else a shot at running
                    lock.release()
                    lock.acquire()
            
     
        print 'new round max %d' % round_max_id
        put_last_max_id(round_max_id) # in case we die, store our state
        max_id = round_max_id

        if num_mentions_run == 0:
            # No new tweets :(
            # just run rainbow i guess
            print 'no tweets, running rainbow'
            handle_rainbow()
            lock.release()
            continue
        
        lock.release()

    #d = driver.Driver()
    #bs = binary.BinaryShifter('Tweet me!')

    while True:
        results = api.search(q='#cseblinkenlights', rpp=1, result_type='recent')
        if len(results) > 0:
            bs.update_text(results[0].text)
 
        while bs.shift():       
            bs.update_pattern()
            time.sleep(1)
    sys.exit(0)

if __name__=="__main__":
    from multiprocessing import Process, Lock
    func(Lock())
