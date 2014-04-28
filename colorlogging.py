#
# Copyright (C) 2010, 2011 Vinay Sajip. All rights reserved.
#
# Source: http://plumberjack.blogspot.com/2010/12/colorizing-logging-output-in-terminals.html
#
import logging
import os

class ColorizingStreamHandler(logging.StreamHandler):
	# color names to indices
	color_map = {
		'black': 0,
		'red': 1,
		'green': 2,
		'yellow': 3,
		'blue': 4,
		'magenta': 5,
		'cyan': 6,
		'white': 7,
	}

	#levels to (background, foreground, bold/intense)
	level_map = {
		logging.DEBUG: (None, 'blue', False),
		logging.INFO: (None, 'white', False),
		logging.WARNING: (None, 'yellow', False),
		logging.ERROR: (None, 'red', False),
		logging.CRITICAL: ('red', 'white', True),
	}
	csi = '\x1b['
	reset = '\x1b[0m'

	@property
	def is_tty(self):
		isatty = getattr(self.stream, 'isatty', None)
		return isatty and isatty()

	def emit(self, record):
		try:
			message = self.format(record)
			stream = self.stream
			if not self.is_tty:
				stream.write(message)
			else:
				self.output_colorized(message)
			stream.write(getattr(self, 'terminator', '\n'))
			self.flush()
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			self.handleError(record)

	def output_colorized(self, message):
		self.stream.write(message)

	def colorize(self, message, record):
		if record.levelno in self.level_map:
			bg, fg, bold = self.level_map[record.levelno]
			params = []
			if bg in self.color_map:
				params.append(str(self.color_map[bg] + 40))
			if fg in self.color_map:
				params.append(str(self.color_map[fg] + 30))
			if bold:
				params.append('1')
			if params:
				message = ''.join((self.csi, ';'.join(params),
								   'm', message, self.reset))
		return message

	def format(self, record):
		message = logging.StreamHandler.format(self, record)
		if self.is_tty:
			# Don't colorize any traceback
			parts = message.split('\n', 1)
			parts[0] = self.colorize(parts[0], record)
			message = '\n'.join(parts)
		return message


#added by jim - source stackoverflow.com/questions/384076
class ColourFormatter(logging.Formatter):
  FORMAT = ("[$BOLD%(name)-20s$RESET][%(levelname)-18s]  "
            "%(message)s "
            "($BOLD%(filename)s$RESET:%(lineno)d)")

  BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

  RESET_SEQ = "\033[0m"
  COLOR_SEQ = "\033[1;%dm"
  BOLD_SEQ = "\033[1m"

  COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
  }

  def formatter_msg(self, msg, use_color = True):
    if use_color:
      msg = msg.replace("$RESET", self.RESET_SEQ).replace("$BOLD", self.BOLD_SEQ)
    else:
      msg = msg.replace("$RESET", "").replace("$BOLD", "")
    return msg

  def __init__(self, use_color=True):
    msg = self.formatter_msg(self.FORMAT, use_color)
    logging.Formatter.__init__(self, msg)
    self.use_color = use_color

  def format(self, record):
    levelname = record.levelname
    if self.use_color and levelname in self.COLORS:
      fore_color = 30 + self.COLORS[levelname]
      levelname_color = self.COLOR_SEQ % fore_color + levelname + self.RESET_SEQ
      record.levelname = levelname_color
    return logging.Formatter.format(self, record)
