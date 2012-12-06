#!/usr/bin/python

import time
import struct
import socket
import threading
import SocketServer

import driver

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		#d = driver.Driver()

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
This will start a 10 second timer. During your 10 seconds, I'll forward
every command you send directly to the strand.

Controlling the bulbs is a 5-byte tuple:
 bulb_id [0-99]
 brightness [0-255]
 green [0-15]
 blue [0-15]
 red [0-15]

You don't need any form of control characters between bulb tuples (no \\0
or anything like that). If you want to give up the strand before your 10
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
		self.request.sendall("Go Time!\\0")

		start = time.time()

		while True:
			if time.time() - start > 10:
				print "User " + name + " timed out"
				self.request.sendall("Time's up!\\0")
				return
			resp = self.request.recv(5, socket.MSG_WAITALL)
			#print "got (len %d) >>>%s<<<" % (len(resp), resp)
			if len(resp) == 0:
				return
			id, bri, grn, red, blu = struct.unpack("BBBBB", resp)
			#d.write_led(id, bri, grn, red, blu)
			print "Would set bulb %d to brightness %d with GRB %d %d %d" % (id, bri, grn, red, blu)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

if __name__ == '__main__':
	HOST, PORT = "0.0.0.0", 4908

	server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
	server.serve_forever()
