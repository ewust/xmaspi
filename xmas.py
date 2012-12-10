#!/usr/bin/python

from multiprocessing import Process, Lock, Value
import command_me
import twitter
import rainbow
import bored
import logger

def main():
    logger.setLogLevel(logger.DEBUG)

    l = Lock()
    cur_running = Value('d', 0)
    p_command_me = Process(target=command_me.func, args=(l,))
    p_ewust = Process(target=twitter.func,args=(l,))
    p_rainbow = Process(target=rainbow.func, args=(l,cur_running, 1))

    p_bored = Process(target=bored.func, args=(l, cur_running, 2))


    p_command_me.start()
    p_ewust.start()
    p_rainbow.start()
    p_bored.start()

    print 'All process start()\'s invoked'

    p_command_me.join()
    p_ewust.join()
    p_rainbow.join()
    p_bored.join()

if __name__ == "__main__":
    main()
