#!/usr/bin/python


import sys

MAX_COLOR = 255
MIN_COLOR = 0
MAX_BRIGHT = 255
MIN_BRIGHT = 0

class Bulb(object):

	def __init__(self, addr, brightness = None, red = None, green = None, blue = None):
		if (brightness is None):
			brightness = 255
		if (red is None):
			red = 255
		if (green is None):
			green = 255
		if (blue is None):
			blue = 255
		self.addr = addr
		self.brightness = brightness 
		self.red = red
		self.green = green
		self.blue = blue

	def update_bulb():
		f = open("/dev/xmas", "w")
		f.write(chr(self.addr) + chr(self.brightness) + chr(self.green) + chr(self.blue) + chr(self.red))
		f.close()

	# Directly set values

	def set_color(red, green, blue):
		self.red = red
		self.green = green
		self.blue = blue
		update_bulb()

	def set_brightness(brightness):
		self.brightness = brightness
		update_bulb()
	
	def dim_to(lower_brightness):
		while (self.brightness > lower_brightness && self.brightness >= MIN_BRIGHT):
			step_down_brightness()

	def brighten_to(higher_brightness):
		while (self.brightness < higher_brightness && self.brightness <= MAX_BRIGHT):
			step_up_brightness()

	def fade_blue_to(lower_blue):
		while (self.blue > lower_blue && self.blue >= MIN_COLOR):
			step_down_blue()

	def saturate_blue_to(higher_blue):
		while (self.blue < higher_blue && self.blue <= MAX_BRIGHT):
			step_up_blue()

	def fade_green_to(lower_green):
		while (self.green > lower_green && self.green >= MIN_COLOR):
			step_down_green()

	def saturate_green_to(higher_green):
		while (self.green < higher_green && self.green <= MAX_BRIGHT):
			step_up_green()

	def fade_red_to(lower_red):
		while (self.red > lower_red && self.red >= MIN_COLOR):
			step_down_red()

	def saturate_red_to(higher_red):
		while (self.red < higher_red && self.red <= MAX_BRIGHT):
			step_up_red()


	# Step values up or down by one

	def step_down_brightness():
		self.brightness = self.brightness - 1
		if self.brightness < MIN_BRIGHT
			self.brightness = MIN_BRIGHT
		update_bulb()

	def step_up_brightness():
		self.brightness = self.brightness + 1
		if self.brightness > MAX_BRIGHT
			self.brightness = MAX_BRIGHT
		update_bulb()

	def step_down_red():
		self.red = self.red - 1
		if self.red < MIN_COLOR
			self.red = MIN_COLOR
		update_bulb()

	def step_up_red():
		self.red = self.red + 1
		if self.red > MAX_COLOR
			self.red = MAX_COLOR
		update_bulb()

	def step_down_green():
		self.green = self.green - 1
		if self.green < MIN_COLOR
			self.green = MIN_COLOR
		update_bulb()

	def step_up_green():
		self.green = self.green + 1
		if self.green > MAX_COLOR
			self.green = MAX_COLOR
		update_bulb()

	def step_down_blue():
		self.blue = self.blue - 1
		if self.blue < MIN_COLOR
			self.blue = MIN_COLOR
		update_bulb()

	def step_up_blue():
		self.blue = self.blue + 1
		if self.blue > MAX_COLOR
			self.blue = MAX_COLOR
		update_bulb()

