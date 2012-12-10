
import logger
import time


from multiprocessing import Lock, Value
from remote import RemoteDriver
import thread

def start_proc(f):
    logger.info('going to run %s' % f)
    g = globals()
    g['__name__'] = '__main__'
    execfile(f, g)
    logger.info('hmm execfile returned, weird.')



def func(lock, fname, cur_running, my_priority, run_time, sleep_time):
    # let's run driver for 30 seconds:
    RemoteDriver().set_lock(lock, cur_running, my_priority, run_time, sleep_time)
    
    logger.info('Bored starting %s' % (fname))
    thread.start_new_thread(start_proc, (fname,))


    while True:
        time.sleep(5)

    end = time.time() + 30
    while time.time() < end:
        time.sleep(0.1)
    
    # should kill proc in 30 seconds or something
    logger.info('Bored finished. Now what?')

    time.sleep(100)
