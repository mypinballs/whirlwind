import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
from time import strftime
import string
import time
import locale
import math
import copy
import yaml
from loader import *
import logging

#os.chdir("/Users/jim/Documents/Pinball/p-roc/p-roc system/src/pyprocgame/")


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


game_locale = config.value_for_key_path('std_locale')
locale.setlocale(locale.LC_ALL, game_locale) # en_GB Used to put commas in the score.

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/spacemission/"
fonts_path = base_path+"shared/dmd/"
shared_sound_path = base_path+"shared/sound/"

machine_config_path = game_path + "config/machine.yaml"
settings_path = game_path +"config/settings.yaml"
game_data_path = game_path +"config/game_data.yaml"
game_data_template_path = game_path +"config/game_data_template.yaml"
settings_template_path = game_path +"config/settings_template.yaml"

voice_path = game_path +"speech/"
voice_high_score_path = game_path +"speech/highscores/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Game(game.BasicGame):
	"""docstring for Game"""
	def __init__(self, machine_type):
		super(Game, self).__init__(machine_type)
		self.sound = procgame.sound.SoundController(self)
		self.lampctrl = procgame.lamps.LampController(self)
		self.settings = {}

	def save_settings(self):
		#self.write_settings(settings_path)
                super(Game, self).save_settings(settings_path)
		#pass

        def save_game_data(self):
		super(Game, self).save_game_data(game_data_path)
                

	def setup(self):
		"""docstring for setup"""
		self.load_config(self.yamlpath)
                self.load_settings(settings_template_path, settings_path)
		self.sound.music_volume_offset = self.user_settings['Sound']['Music volume offset']
		self.sound.set_volume(self.user_settings['Sound']['Initial volume'])
		self.load_game_data(game_data_template_path, game_data_path)

#		print "Stats:"
#		print self.game_data
#		print "Settings:"
#		print self.settings

                # Setup fonts
		self.fonts = {}
		self.fonts['tiny7'] = dmd.Font(fonts_path+"04B-03-7px.dmd")
 		self.fonts['07x5'] = dmd.Font(fonts_path+"Font07x5.dmd")
                self.fonts['6x6_bold'] = dmd.Font(fonts_path+"Font_6x6_bold.dmd")


		
		# setup modes
		self.loader = Loader(self,2)

		
		# Instead of resetting everything here as well as when a user
		# initiated reset occurs, do everything in self.reset() and call it
		# now and during a user initiated reset.
		self.reset()

	def reset(self):
		# Reset the entire game framework
		super(Game, self).reset()

		# Add the basic modes to the mode queue
		self.modes.add(self.loader)

		# Make sure flippers are off, especially for user initiated resets.
		self.enable_flippers(enable=False)

	
def main():

	config = yaml.load(open(machine_config_path, 'r'))
        print("Using config at: %s "%(machine_config_path))
	machine_type = config['PRGame']['machineType']
	config = 0
	game = None
	try:
	 	game = Game(machine_type)
		game.yamlpath = machine_config_path
		game.setup()
		game.run_loop()
	finally:
		del game


if __name__ == '__main__': main()
