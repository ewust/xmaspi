
import logger
import time


from multiprocessing import Lock, Value, Process
from remote import RemoteDriver
import thread

def start_proc(fname, lock, cur_running, priority, run_time, sleep_time):
    logger.info('going to run %s' % fname)
    RemoteDriver().set_lock(lock, cur_running, priority, run_time, sleep_time)
    g = globals()
    g['__name__'] = '__main__'
    
    execfile(fname, g)
    logger.info('hmm execfile returned, weird.')


# (program, run time, sleep time, priority
progs = [('./xmaspi-client/sine.py', 30, 15),\
    ('./xmaspi-client/snake.py', 30, 30),\
    ('./xmaspi-client/randomwalk.py', 30, 10), \
    ('./xmaspi-client/wheel.py', 30, 90),\
    ('./xmaspi-client/waterfall.py', 30, 10), \
    ('./xmaspi-client/sort.py', 60, 90), \
    #('./xmaspi-client/mergesort.py', 30, 150), \
    ('./xmaspi-client/quicksort.py', 60, 100), \
    #('./xmaspi-client/clock.py', 60, 100)\
    ]



def func(lock, cur_running, my_priority):
    # let's run driver for 30 seconds:
    
    while True:
        idx = 0
        for (fname, run_time, sleep_time) in progs: 
            idx += 1
            logger.info('Bored starting %s (prio %d, cur %d)' % (fname, my_priority+idx, cur_running.value))
    
            p_bored = Process(target=start_proc, args=(fname, lock, cur_running,my_priority+idx, run_time, sleep_time))
            
            p_bored.start()
            #thread.start_new_thread(start_proc, (fname,))
            

            end = time.time() + run_time
            while time.time() < end:
                time.sleep(0.1)
            # Must take lock from them before we kill them
            # so they don't die with the lock held
            logger.debug("Bored acquiring lock to kill %s...(cur running: %d)" % (fname, cur_running.value))
            lock.acquire()

            p_bored.terminate()

            # clean up after last running process
            if cur_running.value == my_priority + idx:
                logger.debug("Had to set cur running value from %d to 0" % (cur_running.value))
                cur_running.value = 0 
            logger.debug("Bored releasing lock (cur: %d)" % cur_running.value)
            lock.release()

            time.sleep(10) 
