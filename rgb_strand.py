#!/usr/bin/python


import sys
import bulb
import driver

BROADCAST = -1

class RGBStrand(object):

    def __init__(self, num_bulbs = None):
        d = driver.Driver() 
        if (num_bulbs is None):
            num_bulbs = 50
        self.num_bulbs = num_bulbs  
        self.bulbs = []
        for id in range(num_bulbs):
            self.bulbs.append(bulb.Bulb(id, d))
        self.broadcast = bulb.Bulb(BROADCAST, d)

    # Individual bulb commands

    def set_bulb_attributes(self, id, brightness, red, green, blue):
        self.bulbs[id].set_brightness(brightness)
        self.bulbs[id].set_color(red, green, blue)  

    def set_bulb_color(self, id, red, green, blue):
        self.bulbs[id].set_color(red, green, blue)
    
    def set_bulb_brightness(self, id, brightness):
        self.bulbs[id].set_brightness(brightness)

    def brighten_bulb_to(self, id, higher_brightness, rate=1):
        self.bulbs[id].brighten_to(higher_brightness, rate)

    def dim_bulb_to(self, id, lower_brightness, rate=1):
        self.bulbs[id].dim_to(lower_brightness, rate)

    # Synchronized strand commands
    
    def set_strand_color(self, red, green, blue):
        self.cascading_strand_color(red, green, blue)

    def set_strand_brightness(self, brightness):
        self.broadcast.set_brightness(brightness)
    
    def brighten_strand(self, higher_brightness, rate=1):
        self.broadcast.brighten_to(higher_brightness, rate)
    
    def dim_strand(self, lower_brightness, rate=1):
        self.broadcast.dim_to(lower_brightness, rate)

    # Cascading commands, can do every mod  

    def cascading_strand_color(self, red, green, blue, mod=1):
        for id in range(0, self.num_bulbs, mod):
            self.set_bulb_color(id, red, green, blue)

    def cascading_strand_brightness(self, brightness, mod=1):
        for id in range(0, self.num_bulbs, mod):
            self.set_bulb_brightness(id, brightness)

    def cascading_dim_strand(self, lower_brightness, rate=1, mod=1):
        for id in range(0, self.num_bulbs, mod):
            self.dim_bulb_to(id, lower_brightness, rate)

    def cascading_brighten_strand(self, higher_brightness, rate=1, mod=1):
        for id in range(0, self.num_bulbs, mod):
            self.brighten_bulb_to(id, higher_brightness, rate)

    def set_strand_pattern(self, color_array):
        for i in range(self.num_bulbs):
            rgb = color_array[i % len(color_array)]
            self.set_bulb_color(i, rgb[0], rgb[1], rgb[2])


# Smooth transitions between colors not happening for some reason 
    def fade_bulb_color(self, id, channel, lower_val):
        if (channel == 'r'):
            self.bulbs[id].fade_red_to(lower_val)
        elif (channel == 'g'):
            self.bulbs[id].fade_green_to(lower_val)
        elif (channel == 'b'):
            self.bulbs[id].fade_blue_to(lower_val)
        else:
            print "Not a valid channel. Choose from r, g, or b."

    def saturate_bulb_color(self, id, channel, higher_val):
        if (channel == 'r'):
            self.bulbs[id].saturate_red_to(lower_val)
        elif (channel == 'g'):
            self.bulbs[id].saturate_green_to(lower_val)
        elif (channel == 'b'):
            self.bulbs[id].saturate_blue_to(lower_val)
        else:
            print "Not a valid channel. Choose from r, g, or b."

    def fade_strand_color(self, channel, lower_val, mod = 1):
        for id in range(0, self.num_bulbs, mod):
            self.fade_bulb_color(id, channel, lower_val)    

    def saturate_strand_color(self, channel, higher_val, mod = 1):
        for id in range(0, self.num_bulbs, mod):
            self.saturate_bulb_color(id, channel, lower_val)    

    def scroll_back(self):
        for id in reversed(range(1,self.num_bulbs)):
            b = self.bulbs[id]
            self.set_bulb_attributes(id-1, b.brightness, b.red, b.green, b.blue)

    def scroll_forward(self):
        for id in reversed(range(0,self.num_bulbs-1)):
            b = self.bulbs[id]
            self.set_bulb_attributes(id+1, b.brightness, b.red, b.green, b.blue)

    def push_top(self, brightness, r, g, b):
        self.scroll_forward()
        self.set_bulb_attributes(0, brightness, r, g, b)

    def push_bottom(self, brightness, r, g, b):
        self.scroll_back()
        self.set_bulb_attributes(self.num_bulbs-1, brightness, r, g, b)

    def turn_off(self):
        self.set_strand_brightness(0)

    def turn_on(self):
        self.set_strand_brightness(MAX_BRIGHT)
