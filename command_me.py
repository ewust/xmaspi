#!/usr/bin/python

import sys
import traceback
import time
import struct
import socket
import threading
import logger
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
            self.name = name.strip()
            logger.info("'%s' connected from %s:%d" % (self.name, self.client_address[0], self.client_address[1]))

        name = name[:-1]
        if len(name) == 0:
            self.request.sendall("I won't talk to you if you don't tell me who you are.\n")
            self.request.sendall("Try sending a name next time. Goodbye.\n")
            return

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
            logger.info("%s (%s:%d) didn't send 'let's go'" % \
                (self.name, self.client_address[0], self.client_address[1]))
            return

        self.request.settimeout(1)

        # Block for controller here
        logger.debug("Remote me ('%s' %s:%d) acquiring lock..." % \
            (self.name, self.client_address[0], self.client_address[1]))
        glock.acquire()
        try:
            logger.info('Got lock; running %s (%s:%d)' % \
                (self.name, self.client_address[0], self.client_address[1]))
            self.request.sendall("Go Time!\n")

            start = time.time()

            while True:
                if time.time() - start > 30:
                    logger.info("%s (%s:%d) timed out" % \
                        (self.name, self.client_address[0], self.client_address[1]))
                    self.request.sendall("Time's up!\n")
                    return
                resp = self.request.recv(5, socket.MSG_WAITALL)
                #print "got (len %d) >>>%s<<<" % (len(resp), resp)
                if len(resp) == 0:
                    logger.info("%s (%s:%d) closed the connection" % \
                        (self.name, self.client_address[0], self.client_address[1]))
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
                    logger.debug("Would set bulb %d to brightness %d with RGB %d %d %d" % (id, bri, red, grn, blu))
        except socket.timeout:
            logger.info("%s (%s:%d) timed out on sending me a packet" % \
                (self.name, self.client_address[0], self.client_address[1]))
            
            self.request.sendall("You took too long to send me a packet. Goodbye!\n")
            return
        except:
            
            logger.info("%s (%s:%d) threw an exception:" % \
                (self.name, self.client_address[0], self.client_address[1]))
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            return
        finally:
            logger.debug("Remote me ('%s' %s:%d) releasing lock..." % \
                (self.name, self.client_address[0], self.client_address[1]))
            glock.release()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

def func(lock):
    logger.info("Spawning command_me...")

    HOST, PORT = "0.0.0.0", 4908

    global glock
    glock = lock

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.serve_forever()

if __name__ == '__main__':
    lock = Lock()
    Process(target=func, args=(lock,)).start()
