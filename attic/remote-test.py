
from remote import RemoteDriver
import time

print 'why no work'
print "what name are we: %s" % __name__

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
 
