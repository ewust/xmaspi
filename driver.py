#!/usr/bin/python

STRAND_LEN = 50

# Keeps a mapping between LED Ids (0-N*50) to (strand, addr) pairs
class Driver(object):

    # Strand orientations are arrays of either 1 or -1,
    # for each strand.
    # A strand with a -1 orientation will address 
    def __init__(self, num_strands=1, strand_orientations=None, strand_order=None, do_init=False):
        self.num_strands = num_strands 
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
                    self.send_pkt((index, addr), 0, 0, 0, 0)
                addr += orientation
                led_id += 1
 

    def send_pkt(phys_addr, brightness, green, blue, red):
        f = open('/dev/xmas', 'w')
        f.write(chr((phys_addr[0] << 6) | phys_addr[1]) + chr(brightness) + chr(green) + chr(blue) + chr(red))
        f.close()

    # get a physical address tuple from an LED ID
    # returns (strand, addr)
    def get_physical_addr(self, led_id):
        return self.phys_addr[led_id]


    def write_led(led_id, brightness, green, blue, red):
        # get physical address
        self.send_pkt(self.get_physical_addr(led_id), brightness, green, blue, red)
    


if __name__=="__main__":
    # Test
    d = Driver(2, [-1, 1], [0, 1])
    d.write_led(0, 200, 15, 0, 0)
    d.write_led(99, 200, 0, 0, 15)
