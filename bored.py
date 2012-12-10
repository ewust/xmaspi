
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


# (program, run time, sleep time, priority
progs = [('./xmaspi-client/sine.py', 30, 90),\
    ('./xmaspi-client/snake.py', 30, 90),\
    #('./xmaspi-client/wheel.py', 30, 90),\
    #('./xmaspi-client/sort.py', 30, 90), \
    #('./xmaspi-client/mergesort.py', 30, 150), \
    #('./xmaspi-client/quicksort.py', 50, 100)]
    ]



def func(lock, cur_running, my_priority):
    # let's run driver for 30 seconds:
    
    while True:
        idx = 0
        for (fname, run_time, sleep_time) in progs:
            RemoteDriver().set_lock(lock, cur_running, my_priority+idx, run_time, sleep_time)
            
            idx += 1
            logger.info('Bored starting %s' % (fname))
            thread.start_new_thread(start_proc, (fname,))
             


            end = time.time() + run_time
            while time.time() < end:
                time.sleep(0.1)
            logger.info('Bored: %s should be done' % (fname))
            time.sleep(3) 

        while True:
            time.sleep(1000)
