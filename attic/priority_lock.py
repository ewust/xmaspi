
from multiprocessing import Lock, Value, Process


currently_running = False
sleep_time = 0



# Run this in a loop. Actually, I'll do it for you.
def acquire_lock_priority(lock, cur_running, my_priority, run_time, off_time, name=''):
    global currently_running, sleep_time
    while True:
        if cur_running.value > my_priority:
            time.sleep(.1)
            currently_running = False
            continue

        lock.acquire()
        #print '%s--got lock cur %d mine %d' % (name, cur_running.value, my_priority)
        
        # double check with lock
        if cur_running.value > my_priority:
            # race on the lock and we lost
            # try again
            lock.release()
            #print '%s not my lock' % name
            time.sleep(0.1) # and don't let it happen again
            continue

        if not currently_running:
            currently_running = True  
            sleep_time = time.time() + run_time
            cur_running.value = my_priority

        if time.time() > sleep_time:
            # Bed time, release lock sleep, restart loop
            cur_running.value = 0
            lock.release() 
            #print '%s releasing' % name
            if off_time != 0:
                time.sleep(off_time)
            #time.sleep(0.0) # higher for others, but rainbow never sleeps
            currently_running = False
            continue

        if currently_running:
            break
    #print '%s returning cur %d mine %d' % (name, cur_running.value, my_priority)
 


# TEST:

import time

def f1(lock, cur_running, my_priority):
    n = 0
    while True:
        acquire_lock_priority(lock, cur_running, my_priority, 10, 10, 'f1')
        print 'A %d' % n
        n+= 1
        lock.release()
        time.sleep(1)

def f2(lock, cur_running, my_priority):
    n = 0
    while True:
        acquire_lock_priority(lock, cur_running, my_priority, 5, 12, 'f2')
        print 'B %d' % n
        n+= 1
        lock.release()
        time.sleep(1)


def background(lock, cur_running, my_priority):
    n = 0
    while True:
        acquire_lock_priority(lock, cur_running, my_priority, 30, 0, 'back')
        print 'nobody %d' % n
        n+= 1
        lock.release()
        time.sleep(1)        

if __name__=='__main__':
    cur_running = Value('d', 0)
    lock = Lock()
    
    p1 = Process(target=f1, args=(lock, cur_running, 10))
    p2 = Process(target=f2, args=(lock, cur_running, 20))
    p3 = Process(target=background, args=(lock, cur_running, 1))

    p1.start()
    p2.start()
    p3.start()
    
    p1.join()
    p2.join()    
    p3.join()
    
