
import logger
import time


from multiprocessing import Lock, Value
from remote import RemoteDriver
import thread

def start_proc(f):
    execfile(f, globals())
    logger.info('hmm execfile returned, weird.')

def func(lock, cur_running, my_priority):
    # let's run driver for 30 seconds:
    RemoteDriver().set_lock(lock, cur_running, my_priority, 30, 1000)
    
    logger.info('Bored Sleeping for 5...')
    time.sleep(5)
    logger.info("Bored...running remote (don't crash on me!)")
    thread.start_new_thread(start_proc, ('remote.py',))

    end = time.time() + 30
    while time.time() < end:
        time.sleep(0.1)
    
    # should kill proc in 30 seconds or something
    logger.info('Bored finished. Now what?')

    time.sleep(100)
