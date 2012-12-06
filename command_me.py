#!/usr/bin/python

import sys
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

		self.request.settimeout(1)

		name = self.request.recv(1)
		while True:
			if name[-1] == '\0':
				break
			elif name[-1] == '\n':
				self.request.sendall("I don't like newlines.\r\n")
				return
			elif len(name) == 16:
				return
			name += self.request.recv(1)

		print "Request from", name
		# parse
		self.request.sendall("Hi " + name + "!\n")
		self.request.sendall("""
You've found the Bob and Betty Beyster Bright Blinken Bulbs API!

Once you're ready to control the strand, send the 9 bytes
  >>>let's go\\0<<<
back to me. I'll enqueue you to control the strand. When it's your
turn, I'll send you the 9 bytes
  >>>Go Time!\\0<<<
This will start a 30 second timer. During your 30 seconds, I'll forward
every command you send directly to the strand.

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
		if resp != "let's go\0":
			print "Didn't get let's go, got:"
			print ">>>%s<<<" % (resp)
			return

		# Block for controller here
		glock.acquire()
		try:
			self.request.sendall("Go Time!\\0")

			start = time.time()

			while True:
				if time.time() - start > 30:
					glock.release()
					print "User " + name + " timed out"
					self.request.sendall("Time's up!\\0")
					return
				resp = self.request.recv(5, socket.MSG_WAITALL)
				#print "got (len %d) >>>%s<<<" % (len(resp), resp)
				if len(resp) == 0:
					glock.release()
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
		except:
			glock.release()
			print "User " + name + " threw an exception"
			return

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

def command_me(lock):
	HOST, PORT = "0.0.0.0", 4908

	global glock
	glock = lock

	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	server.serve_forever()

if __name__ == '__main__':
	lock = Lock()
	Process(target=command_me, args=(lock,)).start()
