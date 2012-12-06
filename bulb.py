#!/usr/bin/python


import sys
import driver

MAX_COLOR = 255
MIN_COLOR = 0
MAX_BRIGHT = 255
MIN_BRIGHT = 0

class Bulb(object):

	def __init__(self, id, driver, brightness = None, red = None, green = None, blue = None):
		if (brightness is None):
			brightness = MAX_BRIGHT
		if (red is None):
			red = MAX_COLOR
		if (green is None):
			green = MAX_COLOR
		if (blue is None):
			blue = MAX_COLOR
		self.id = id
		self.brightness = brightness 
		self.red = red
		self.green = green
		self.blue = blue
		self.driver = driver

	def update_bulb(self):
		self.driver.write_led(self.id, self.brightness, self.blue, self.green, self.red)
	
	# Directly set values

	def set_all(self, brightness, red, green, blue):
		self.set_brightness(brightness)
		self.set_color(red, green, blue)

	def set_color(self, red, green, blue):
		self.red = red
		self.green = green
		self.blue = blue
		self.update_bulb()

	def set_brightness(self, brightness):
		self.brightness = brightness
		self.update_bulb()
	
	def dim_to(self, lower_brightness, step=1):
		while (self.brightness > lower_brightness and self.brightness >= MIN_BRIGHT):
			self.step_down_brightness(step)

	def brighten_to(self, higher_brightness, step=1):
		while (self.brightness < higher_brightness and self.brightness <= MAX_BRIGHT):
			self.step_up_brightness(step)

	def fade_blue_to(self, lower_blue):
		while (self.blue > lower_blue and self.blue >= MIN_COLOR):
			self.step_down_blue()

	def saturate_blue_to(self, higher_blue):
		while (self.blue < higher_blue and self.blue <= MAX_BRIGHT):
			self.step_up_blue()

	def fade_green_to(self, lower_green):
		while (self.green > lower_green and self.green >= MIN_COLOR):
			self.step_down_green()

	def saturate_green_to(self, higher_green):
		while (self.green < higher_green and self.green <= MAX_BRIGHT):
			self.step_up_green()

	def fade_red_to(self, lower_red):
		while (self.red > lower_red and self.red >= MIN_COLOR):
			self.step_down_red()

	def saturate_red_to(self, higher_red):
		while (self.red < higher_red and self.red <= MAX_BRIGHT):
			self.step_up_red()


	# Step values up or down by one

	def step_down_brightness(self, amount=1):
		self.brightness = self.brightness - amount
		if self.brightness < MIN_BRIGHT:
			self.brightness = MIN_BRIGHT
		self.update_bulb()

	def step_up_brightness(self, amount=1):
		self.brightness = self.brightness + amount
		if self.brightness > MAX_BRIGHT:
			self.brightness = MAX_BRIGHT
		self.update_bulb()

	def step_down_red(self, amount=1):
		self.red = self.red - amount
		if self.red < MIN_COLOR:
			self.red = MIN_COLOR
		self.update_bulb()
	
	def step_up_red(self, amount=1):	
		self.red = self.red + amount
		if self.red > MAX_COLOR:
			self.red = MAX_COLOR
		self.update_bulb()

	def step_down_green(self, amount=1):
		self.green = self.green - amount
		if self.green < MIN_COLOR:
			self.green = MIN_COLOR
		self.update_bulb()

	def step_up_green(self, amount=1):
		self.green = self.green + amount
		if self.green > MAX_COLOR:
			self.green = MAX_COLOR
		self.update_bulb()

	def step_down_blue(self, amount=1):
		self.blue = self.blue - amount
		if self.blue < MIN_COLOR:
			self.blue = MIN_COLOR
		self.update_bulb()

	def step_up_blue(self, amount=1):
		self.blue = self.blue + amount
		if self.blue > MAX_COLOR:
			self.blue = MAX_COLOR
		self.update_bulb()

