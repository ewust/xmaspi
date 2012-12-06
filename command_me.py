#!/usr/bin/python

import sys
import traceback
import time
import struct
import socket
import threading
import SocketServer

from multiprocessing import Process, Lock

import driver

global glock

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		global glock
		if len(sys.argv) == 1:
			d = driver.Driver()

		try:
			name = self.request.recv(1)
			while True:
				if name[-1] in ('\0', '\n'):
					break
				elif len(name) == 16:
					return
				resp = self.request.recv(1)
				if len(resp):
					name += resp
				else:
					return
		finally:
			print 'Got %d byte name >>>%s<<<' % (len(name), name)

		name = name[:-1]
		if len(name) == 0:
			self.request.sendall("I won't talk to you if you don't tell me who you are.\n")
			self.request.sendall("Try sending a name next time. Goodbye.\n")
			return

		print "Request from", name
		# parse
		self.request.sendall("Hi " + name + "\n")
		self.request.sendall("""
You've found the Bob and Betty Beyster Bright Blinken Bulbs API!

Once you're ready to control the strand, send the 9 bytes
  >>>let's go\\n<<<
back to me. I'll enqueue you to control the strand. When it's your
turn, I'll send you the 9 bytes
  >>>Go Time!\\n<<<
This will start a 30 second timer. During your 30 seconds, I'll forward
every command you send directly to the strand. You'll need to send at least
one packet every second to keep your session alive.

Controlling the bulbs is a 5-byte tuple:
 bulb_id [0-99]
 brightness [0-255]
 red [0-15]
 green [0-15]
 blue [0-15]

You don't need any form of control characters between bulb tuples (no \\0
or anything like that). If you want to give up the strand before your 30
seconds runs out, just close the connection.

Looking forward to your creations! :)
\0
""")

		resp = self.request.recv(9)
		if resp != "let's go\n":
			self.request.sendall("I didn't get let's go\\n, I got:\n")
			self.request.sendall(resp)
			print "Didn't get let's go, got:"
			print ">>>%s<<<" % (resp)
			return

		self.request.settimeout(1)

		# Block for controller here
		glock.acquire()
		try:
			self.request.sendall("Go Time!\n")

			start = time.time()

			while True:
				if time.time() - start > 30:
					print "User " + name + " timed out"
					self.request.sendall("Time's up!\\0")
					return
				resp = self.request.recv(5, socket.MSG_WAITALL)
				#print "got (len %d) >>>%s<<<" % (len(resp), resp)
				if len(resp) == 0:
					print "User " + name + " closed connection"
					return
				id, bri, red, grn, blu = struct.unpack("BBBBB", resp)
				if id > 99 or grn > 15 or blu > 15 or red > 15:
					if len(sys.argv) > 1:
						print "Invalid parameter, skipping message"
						print "bulb %d brightness %d RGB %d %d %d" % (id, bri, red, grn, blu)
					self.request.sendall("Invalid parameter, skipped\\0")
					continue
				if len(sys.argv) == 1:
					d.write_led(id, bri, blu, grn, red)
				else:
					print "Would set bulb %d to brightness %d with RGB %d %d %d" % (id, bri, red, grn, blu)
		except socket.timeout:
			print "User " + name + " timed out on sending me a packet"
			self.request.sendall("You took too long to send me a packet. Goodbye!\n")
			return
		except:
			print "User " + name + " threw an exception"
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
			return
		finally:
			glock.release()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

def func(lock):
	print "Spawning command_me..."

	HOST, PORT = "0.0.0.0", 4908

	global glock
	glock = lock

	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	server.serve_forever()

if __name__ == '__main__':
	lock = Lock()
	Process(target=func, args=(lock,)).start()
