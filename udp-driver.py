#!/usr/bin/python
import socket
import sys
import time
import struct
import select


NUM_LIGHTS = 100


STRAND_LEN = 50


class UdpDriver(object):
    def __init__(self, fname='/dev/xmas', port=1337):
        self.f = open(fname, 'w')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        self.sock.setblocking(0)
        self.state = ['\x00\x00\x00\x00']*NUM_LIGHTS
        self.addr_to_phys_id = [0]*NUM_LIGHTS
        for idx in range(NUM_LIGHTS):
            if idx < 50:
                self.addr_to_phys_id[idx] = 49-idx
            else:
                self.addr_to_phys_id[idx] = (idx - 50) | 0x40
                #self.addr_to_phys_id[idx] = (100-idx) | 0x40


    def get_latest_packet(self):
        ret = None
        while True:
            try:
                data,addr = self.sock.recvfrom(NUM_LIGHTS*4)
                ret = data
            except socket.error:
                if ret == None:
                    select.select([self.sock], [], [])
                    continue
                #print 'data = %s' % data
                return ret

    # returns the string you need to send to /dev/xmas
    # this allows you to buffer all changes per frame and then send the whole frame
    def update_bulb(self, idx, new_state):
        (brightness, r, g, b) = struct.unpack('BBBB', new_state)
        bulb_id = self.addr_to_phys_id[idx]
        #print 'idx %d -> id %d (%d, %d, %d, %d)' % (idx, bulb_id, brightness, r, g, b)
        return chr(bulb_id) + chr(brightness) + chr(b) + chr(g) + chr(r)

    def new_frame(self, data):
        buf = ''
        for i in range(NUM_LIGHTS):
            new_state = data[4*i:4*(i+1)]
            # compare to current state
            if new_state != self.state[i]:
                self.state[i] = new_state

                # write to /dev/xmas
                buf += self.update_bulb(i, new_state)
        if buf != '':
            self.f.write(buf)
            self.f.flush()
        return buf != ''


if __name__ == '__main__':
    port = 1337
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    d = UdpDriver(port=port)
    while True:
        data = d.get_latest_packet()
        if data != None:
            if len(data) == 400:
                d.new_frame(data)
