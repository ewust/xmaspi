#!/usr/bin/python

from multiprocessing import Process, Lock, Value
import command_me
import twitter
import rainbow
import bored

# (program, run time, sleep time, priority
progs = [('./xmaspi-client/sine.py', 30, 90, 2),\
    ('./xmaspi-client/snake.py', 30, 90, 3),\
    ('./xmaspi-client/wheel.py', 30, 90, 4),\
    ('./xmaspi-client/sort.py', 30, 90, 5), \
    ('./xmaspi-client/mergesort.py', 30, 150, 6), \
    ('./xmaspi-client/quicksort.py', 50, 100, 7)]


def main():
    l = Lock()
    cur_running = Value('d', 0)
    p_command_me = Process(target=command_me.func, args=(l,))
    p_ewust = Process(target=twitter.func,args=(l,))
    p_rainbow = Process(target=rainbow.func, args=(l,cur_running, 1))

    p_bored = []
    for (fname, run_time, sleep_time, priority) in progs:
        p = Process(target=bored.func, args=(l, fname, cur_running, priority, run_time, sleep_time))
        p_bored.append(p)


    p_command_me.start()
    p_ewust.start()
    p_rainbow.start()
    for p in p_bored:
        p.start()

    print 'All process start()\'s invoked'

    p_command_me.join()
    p_ewust.join()
    p_rainbow.join()
    for p in p_bored:
        p.join()

if __name__ == "__main__":
    main()
