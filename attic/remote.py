#!/usr/bin/python

import socket
import time
import sys
import traceback
import getpass
import logger
from priority_lock import acquire_lock_priority
from driver import Driver

# This is a Shim between a xmaspi-client RemoteDriver
# that adapts it to the local RaspberryPi Driver
# and allows the task to run as a background task for N seconds at a time
class RemoteDriver(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RemoteDriver, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

 
    lock = None
    def __init__(self, name=None, addr="141.212.110.237", port=4908):
        #Driver().
        # TOOD: call Driver().gimme_lock_info(self) (and implement it)
        pass

    def go(self):
        pass

    # Not called from the user's program, but rather the background process    
    def set_lock(self, lock, cur_running, my_priority, run_time, off_time):
        # Thanks!
        self.lock = lock
        self.cur_running = cur_running
        self.my_priority = my_priority
        self.run_time = run_time
        self.off_time = off_time
        self.next_acquire_time = time.time()
        self.have_lock = False
        self.driver = Driver()

    def write_led(self, led_id, brightness, red, green, blue):
        # every once in a while, we should release the lock
        if time.time() > self.next_acquire_time:
            #if self.have_lock:
            #    self.lock.release()
            acquire_lock_priority(self.lock, self.cur_running, self.my_priority, self.run_time, self.off_time)
            self.lock.release() # can't hold lock in case user calls sleep
            #self.have_lock = True # just true after the first time 
            self.next_acquire_time = time.time() + 0.01
    
        self.driver.write_led(led_id, brightness, blue, green, red)

    def busy_wait(self, duration=None):
        if duration is None:
            duration = 100

        while duration > 0:
            try:
                #self.write_led(100, 0, 0, 0, 0)
                acquire_lock_priority(self.lock, self.cur_running, self.my_priority, self.run_time, self.off_time) 
                self.lock.release()
                 

                time.sleep(min(duration, 0.5))
                duration -= 0.5
            except:
                return
    wait = busy_wait

    def stop_signal(self):
        """
        Returns True if client's turn is over
        (use for future compatibility)
        """
        return False

    def done(self):
        # We should probably do something like...
        # release the lock and sleep?
        pass
        


if __name__=="__main__":
    # Unit Test/Example Use:

    # This will block until it is your turn 
    print 'Waiting for our turn...'
    d = RemoteDriver("UnitTest")
    print 'Our turn!'

    # Turn off all the LEDs 
    for i in range(100):
        d.write_led(i, 0, 0, 0, 0)

    # Turn them back on from the top, with some delay (100*.05 = 5s)
    for i in range(100):
        d.write_led(i, 200, 13, 0, 13)
        time.sleep(.05)

    # Turn them off in chunks of 10 (10*2 = 20s)
    # Note that busy_wait must be used for delays >= 1s
    for i in range(100, 0, -10):
        for j in range(i, i-10, -1):
            d.write_led(j-1, 0, 0, 0, 0)
        d.busy_wait(2)

    # Turn on all the LEDs 
    for i in range(100):
        d.write_led(i, 200, 13, 13, 13)
    
    # Send NOP keep-alives until our 30-second time expires
    # Alternatively, you can close the connection with
    # d.done() (or wait for it to time you out)
    d.busy_wait()
 
