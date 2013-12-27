__author__="jim"
__date__ ="$30/01/2013$"

import procgame
import locale
import random

from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"

#possible method to linkup layered display.
#using frame.set_dot method here to record 2x16 chars?
#need subclassed frame method to write out to aux port??
class AlphanumericTextLayer(dmd.TextLayer):

        fill_color = None
	"""Dot value to fill the frame with.  Requres that ``width`` and ``height`` be set.  If ``None`` only the font characters will be drawn."""

	def __init__(self, x, y, font, justify="left", opaque=False, width=16, height=2, fill_color=None):
		super(AlphanumericTextLayer, self).__init__(opaque)
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.fill_color = fill_color
		self.font = font
		self.started_at = None
		self.seconds = None # Number of seconds to show the text for
		self.frame = None # Frame that text is rendered into.
		self.frame_old = None
		self.justify = justify
		self.blink_frames = None # Number of frame times to turn frame on/off
		self.blink_frames_counter = 0

	def set_text(self, text, row, seconds=None, blink_frames=None):
		"""Displays the given message for the given number of seconds."""
                self.row = row # param to determine top or bottom display
		self.started_at = None
		self.seconds = seconds
		self.blink_frames = blink_frames
		self.blink_frames_counter = self.blink_frames
		if text == None:
			self.frame = None
		else:
			(w, h) = self.font.size(text)
			x, y = 0, 0
			if self.justify == 'left':
				(x, y) = (0,0)
			elif self.justify == 'right':
				(x, y) = (-w,0)
			elif self.justify == 'center':
				(x, y) = (-w/2,0)

			if self.fill_color != None:
				self.set_target_position(0, 0)
				self.frame = Frame(width=self.width, height=self.height)
				self.frame.fill_rect(0, 0, self.width, self.height, self.fill_color)
				self.font.draw(self.frame, text, self.x + x, self.y + y)
			else:
				self.set_target_position(self.x, self.y)
				(w, h) = self.font.size(text)
				self.frame = AlphaFrame(w, h)#possible subclass to create
                                for index,ch in text:
                                    self.frame.set_dot(index,row,ch) #ch could be ascii code for character if 255 max value allowed
				#self.font.draw(self.frame, text, 0, 0)
				(self.target_x_offset, self.target_y_offset) = (x,y)

		return self

	def next_frame(self):
		if self.started_at == None:
			self.started_at = time.time()
		if (self.seconds != None) and ((self.started_at + self.seconds) < time.time()):
			self.frame = None
		elif self.blink_frames > 0:
			if self.blink_frames_counter == 0:
				self.blink_frames_counter = self.blink_frames
				if self.frame == None:
					self.frame = self.frame_old
				else:
					self.frame_old = self.frame
					self.frame = None
			else:
				self.blink_frames_counter -= 1
		return self.frame

	def is_visible(self):
		return self.frame != None


