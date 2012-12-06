#!/usr/bin/python

from multiprocessing import Process, Lock
import command_me
import twitter
import rainbow

def main():
	l = Lock()
	p_command_me = Process(target=command_me.command_me, args=(l,))
	p_ewust = Process(target=twitter.func,args=(l,))
	p_rainbow = Process(target=rainbow.func, args=(l,))
	p_command_me.start()
	p_ewust.start()
	p_rainbow.start()
	p_command_me.join()
	p_ewust.join()
	p_rainbow.join()

if __name__ == "__main__":
	main()
