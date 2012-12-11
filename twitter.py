#!/usr/bin/python

import tweepy
import driver
import binary
import time
import sys
import rgb_strand
import webcolors
import traceback
import socket
import fcntl
import logger
SIOCGIFADDR = 0x8915
import struct
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


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    saddr = fcntl.ioctl(s.fileno(), SIOCGIFADDR, struct.pack('256s', ifname[:15]))
    return saddr[20:24]

def handle_ip():

    d = driver.Driver()

    wlan_ip = get_interface_ip('wlan1')
    wlan_ip = '\x8d\xd4\x6e\xed'
    bs = binary.BinaryShifter(wlan_ip)

    while bs.shift():
        bs.update_pattern()
        time.sleep(.5)


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

    while bs.shift():
        bs.update_pattern()
        time.sleep(.5)

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


# Ignore duplicate tweet warnings, and do action anyway
def tweet_response(api, mid, msg):
    try:
        api.update_status(msg, mid)
    except:

        pass


def handle_new_mention(lock, api, mention):
    logger.debug("Twitter (%s, %d) acquiring lock..." % \
        (mention.user.screen_name, mention.id))
    lock.acquire()
    
    try:
        tweet = str(mention.text).strip()
        sys.stdout.write('%s: \'%s\': ' % (mention.user.screen_name, tweet))
        if tweet.lower().startswith('@bbb_blinken '):
            cmd = tweet[len('@bbb_blinken '):]

            if cmd.lower().startswith('ip'):
                sys.stdout.write('ip\n')
                tweet_response(api, mention.id, 'Blinken my IP address for @%s' % (mention.user.screen_name))
                handle_ip()

            elif cmd.lower().startswith('all '):
                color = cmd[len('all '):].lower()
                sys.stdout.write('color(%s)\n' % color)
                tweet_response(api, mention.id, 'Setting the strand to %s for @%s' % (color, mention.user.screen_name))
                handle_color(color)

            elif cmd.lower().startswith('rainbow'):
                sys.stdout.write('running rainbow\n')
                tweet_response(api, mention.id, '@%s can taste the rainbow!' % (mention.user.screen_name))
                handle_rainbow()

            elif cmd.lower().startswith('binary '):
                arg = cmd[len('binary '):]
                sys.stdout.write('binary(%s)\n' % arg)
                # This is 'Enjoy!' in binary ASCII
                enjoy_ascii = '01000101 01101110 01101010 01101111 01111001 00100001'
                tweet_response(api, mention.id, '%s @%s' % (enjoy_ascii, mention.user.screen_name))
                handle_binary(arg)
            else:
                sys.stdout.write('\n')
                sys.stdout.write('[unknown cmd, did nothing]')
                tweet_response(api, mention.id, "I don't know that one @%s. Maybe you should hack it for me ;)   http://t.co/WMWzUQiR" % (mention.user.screen_name))
        else:
            sys.stdout.write('\n')
            sys.stdout.write('[tweet did not start with @bbb_blinken, did nothing]')
    except:
        print "Uncaught exception"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
    finally:
        logger.debug("Twitter (%s, %d) releasing lock..." % \
            (mention.user.screen_name, mention.id))
        lock.release()


def func(lock):
    print "Spawning twitter..."

    #l = StdOutListener()
    a = tweepy.OAuthHandler(consumer_key, consumer_secret)
    a.set_access_token(access_token, access_token_secret)
    api = tweepy.API(a)

    max_id = get_last_max_id()

    while True:
        round_max_id = max_id
        num_mentions_run = 0
        try:
            mentions = api.mentions()
        except:
            cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            print '%s Twitter blocked me, sleeping for a while' % cur_time 

            time.sleep(300)
            continue

        for mention in mentions:
            if mention.id > max_id:
                print 'tweet %d > %d' % (mention.id, max_id)
                handle_new_mention(lock, api, mention)
                if mention.id > round_max_id:
                    round_max_id = mention.id
                if num_mentions_run > 0:
                    # give someone else a shot at running
                    time.sleep(1)
     
        put_last_max_id(round_max_id) # in case we die, store our state
        max_id = round_max_id

        if num_mentions_run == 0:
            # No new tweets :(
            # just run rainbow i guess
            time.sleep(20)
            continue

    #d = driver.Driver()
    #bs = binary.BinaryShifter('Tweet me!')

    while True:
        results = api.search(q='#cseblinkenlights', rpp=1, result_type='recent')
        if len(results) > 0:
            bs.update_text(results[0].text)
 
        while bs.shift():       
            bs.update_pattern()
            time.sleep(20)
    sys.exit(0)

if __name__=="__main__":
    from multiprocessing import Process, Lock
    func(Lock())
