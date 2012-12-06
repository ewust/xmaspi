#!/usr/bin/python

from multiprocessing import Process, Lock
import command_me
import twitter

def main():
	l = Lock()
	p_command_me = Process(target=command_me.command_me, args=(l,))
	p_ewust = Process(target=twitter.func,args=(l,))
	p_command_me.start()
	p_ewust.start()
	p_command_me.join()
	p_ewust.join()

if __name__ == "__main__":
	main()
