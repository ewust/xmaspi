
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
            idx += 1
            logger.info('Bored starting %s (prio %d)' % (fname, my_priority+idx))
    
            p_bored = Process(target=start_proc, args=(fname, lock, cur_running,my_priority+idx, run_time - .5, sleep_time))
            
            p_bored.start()
            #thread.start_new_thread(start_proc, (fname,))
            

            end = time.time() + run_time + 0.5
            while time.time() < end:
                time.sleep(0.1)
            p_bored.terminate()
            # join?
            logger.info('Bored: %s should be done' % (fname))
            logger.info('cur_running: %d' % (cur_running.value))
            time.sleep(3) 

            logger.info('cur_running: %d' % (cur_running.value))
