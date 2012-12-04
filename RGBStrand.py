#!/usr/bin/python


import sys
import Bulb as b

class RGBStrand(object):

	def __init__(self, num_bulbs = None):
		if (num_bulbs is None):
			num_bulbs = 50
		self.num_bulbs = num_bulbs	
		self.bulbs = []
		for id in range(num_bulbs):
			self.bulbs.append(b.Bulb(id))

	def set_bulb_color(self, id, red, green, blue):
		self.bulbs[id].set_color(red, green, blue)
	
	def set_bulb_brightness(self, id, brightness):
		self.bulbs[id].set_brightness(brightness)

	def set_strand_color(self, red, green, blue):
		for id in range(self.num_bulbs):
			set_bulb_color(id, red, green, blue)

	def set_strand_brightness(self, brightness):
		for id in range(self.num_bulbs):
			set_bulb_brightness(id, brightness)

	def dim_bulb_to(self, id, lower_brightness):
		self.bulbs[id].dim_to(lower_brightness)

	def brighten_bulb_to(self, id, higher_brightness):
		self.bulbs[id].brighten_to(higher_brightness)

	def dim_strand(self, lower_brightness, mod):
		for id in range(self.num_bulbs):
			self.dim_bulb_to(id, lower_brightness)

	def brighten_strand(self, higher_brightness, mod):
		for id in range(self.num_bulbs):
			self.brighten_bulb_to(id, higher_brightness)

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

#	def move_left():

#	def move_right():

	def turn_off(self):
		self.set_strand_brightness(0)

	def turn_on(self):
		self.set_strand_brightness(MAX_BRIGHT)
