#!/usr/bin/python

STRAND_LEN = 50

# Keeps a mapping between LED Ids (0-N*50) to (strand, addr) pairs
class Driver(object):

    _instance = None
    f = None
    buf = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Driver, cls).__new__(
                                cls, *args, **kwargs)
            cls.f = open('/dev/xmas', 'w')
            cls.buf = ''
        return cls._instance

    # Strand orientations are arrays of either 1 or -1,
    # for each strand.
    # A strand with a -1 orientation will address 
    def __init__(self, strand_orientations=[-1, 1], \
                 strand_order=[0, 1], do_init=False):
        
        self.num_strands = 1
        if strand_orientations != None:
            self.num_strands = len(strand_orientations)
        self.initialize(strand_orientations, strand_order, do_init)
    
        pass

    # Initialize physical address on the strand
    # and the mapping from led_id to physical addr (strand, addr)
    # strand order is either [0, 1] or [1, 0]
    def initialize(self, strand_orientations=None, strand_order=None, do_init=False):
        
        # Default strand orientation ascending
        if strand_orientations == None:
            strand_orientations = [1]*strand_orientations

        if strand_order == None:
            strand_order = [0, 1]

        self.phys_addr = {} 
        led_id = 0
        for index in range(len(strand_orientations)):
            orientation = strand_orientations[index]
            if orientation == 1:
                addr = 0
            else:
                addr = STRAND_LEN - 1

            for i in range(STRAND_LEN):
                self.phys_addr[led_id] = (strand_order[index], addr)
                if do_init == True:
                    self.send_pkt((index, i), 0, 0, 0, 0)
                addr += orientation
                led_id += 1
 
    def buffer_pkt(self, phys_addr, brightness, green, blue, red):
        self.buf += chr((phys_addr[0] << 6) | phys_addr[1]) + chr(brightness) + chr(green) + chr(blue) + chr(red)

    def flush_buffer(self):
        self.f.write(self.buf)
        self.f.flush()
        self.buf = ''

    def send_pkt(self, phys_addr, brightness, green, blue, red):
        self.f.write(chr((phys_addr[0] << 6) | phys_addr[1]) + chr(brightness) + chr(green) + chr(blue) + chr(red))
        self.f.flush()

    # get a physical address tuple from an LED ID
    # returns (strand, addr)
    def get_physical_addr(self, led_id):
        return self.phys_addr[led_id]

    def write_led_buffered(self, led_id, brightness, blue, green, red):
        
        if led_id == -1:
            # Broadcast
            for s in range(self.num_strands):
                self.buffer_pkt((s, 63), brightness, 0, 0, 0)
        else:
            # Unicast
            self.buffer_pkt(self.get_physical_addr(led_id), brightness, blue, green, red)


    def write_led(self, led_id, brightness, blue, green, red):

        if led_id == -1:
            # Broadcast
            for s in range(self.num_strands):
                self.send_pkt((s, 63), brightness, 0, 0, 0)
        elif led_id == 100:
            # nop
            return
        else:
            # Unicast
            self.send_pkt(self.get_physical_addr(led_id), brightness, blue, green, red)

if __name__=="__main__":
    # Test
    import time
    import sys
    d = Driver([-1, 1], [0, 1], len(sys.argv)==1)

    if len(sys.argv) == 1:
        d.write_led(0, 200, 15, 0, 0)
        d.write_led(99, 200, 0, 0, 15)
        for led_id in range(100):
            d.write_led(led_id, 200, 13, 0, 13)
            time.sleep(0.05)
    else:
        d.write_led(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
