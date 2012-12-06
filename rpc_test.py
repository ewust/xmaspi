#!/usr/bin/env python

import socket
import struct
import time

s = socket.socket()
s.connect(("141.212.110.237", 4908))
s.send("hacker1\n")
s.send("let's go\n")

resp = s.recv(1000)
while 'Go Time!\\n' not in resp:
	print "waiting for our turn..."
	time.sleep(.1)
	resp += s.recv(100)

for cnt in range(20):
	for i in range(100):
		s.send(struct.pack("BBBBB", i, 200, 0, 0, 0))
	time.sleep(.3)
	for i in range(100):
		s.send(struct.pack("BBBBB", i, 200, 15, 15, 15))

print "All done!"

s.close()
