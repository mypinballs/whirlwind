import sys
sys.path.append(sys.path[0]+'/../..') # Set the path so we can find procgame.  We are assuming (stupidly?) that the first member is our directory.
import procgame
import pinproc
import string
import time
import locale
import math
import copy
import yaml
import logging

from ac_relay import *
from switched_coils import *
from scoredisplay import *
from effects import *
from extra_ball import *
from service import *
from attract import *
from base import *
from match import *
from tilt import *
from trough import *
from procgame import *
from player import *
from threading import Thread
from time import strftime


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger('whirlwind.alpha_display').setLevel(logging.DEBUG)

#os.chdir("/Users/jim/Documents/Pinball/p-roc/p-roc system/src/pyprocgame/")

game_locale = config.value_for_key_path('std_locale')
locale.setlocale(locale.LC_ALL, game_locale) # en_GB Used to put commas in the score.

#base_path = "/Users/jim/Documents/Pinball/p-roc/p-roc system/src/"
base_path = config.value_for_key_path('base_path')
logging.info("Base Path is: "+base_path)

game_path = base_path+"games/whirlwind/"
fonts_path = base_path+"shared/dmd/"
shared_sound_path = base_path+"shared/sound/"

machine_config_path = game_path + "config/machine.yaml"
settings_path = game_path +"config/settings.yaml"
game_data_path = game_path +"config/game_data.yaml"
game_data_template_path = game_path +"config/game_data_template.yaml"
settings_template_path = game_path +"config/settings_template.yaml"

voice_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"
font_tiny7 = dmd.Font(fonts_path+"04B-03-7px.dmd")
font_jazz18 = dmd.Font(fonts_path+"Jazz18-18px.dmd")
font_14x10 = dmd.Font(fonts_path+"Font14x10.dmd")
font_18x12 = dmd.Font(fonts_path+"Font18x12.dmd")
font_07x4 = dmd.Font(fonts_path+"Font07x4.dmd")
font_07x5 = dmd.Font(fonts_path+"Font07x5.dmd")
font_09Bx7 = dmd.Font(fonts_path+"Font09Bx7.dmd")
font_6x6_bold = dmd.Font(fonts_path+"Font_6x6_bold.dmd")
font_23x12 = dmd.font_named("font_23x12_bold.dmd")





class Game(game.BasicGame):
	"""docstring for Game"""
	def __init__(self, machine_type):
		super(Game, self).__init__(machine_type)#machine_type pinproc.MachineTypePDB

                #setup logging
                self.log = logging.getLogger('whirlwind.game')
                self.logging_enabled = True #value needed for aux port file in pyprocgame


                self.sound = procgame.sound.SoundController(self)
		self.lampctrl = procgame.lamps.LampController(self)
		self.settings = {}

                #temp debug
                for coil in self.coils:
                    self.log.info("Game Config:"+str(coil.name)+" "+str(coil.number))
                for lamp in self.lamps:
                    self.log.info("Game Config:"+str(lamp.name)+" "+str(lamp.number))

                #setup score display
                self.score_display = AlphaScoreDisplay(self, 0)


	def save_settings(self):
		#self.write_settings(settings_path)
                super(Game, self).save_settings(settings_path)
		#pass

        def save_game_data(self):
		super(Game, self).save_game_data(game_data_path)

        def create_player(self, name):
		return Player(name)
                

	def setup(self):
		"""docstring for setup"""
		self.load_config(self.yamlpath)

                self.load_settings(settings_template_path, settings_path)
		self.sound.music_volume_offset = self.user_settings['Sound']['Music volume offset']
		self.sound.set_volume(self.user_settings['Sound']['Initial volume'])
		self.load_game_data(game_data_template_path, game_data_path)

                #define system status var
                self.system_status='power_up'
                self.system_version='0.2.2'
                self.system_name='Whirlwind 2'.upper()

                #update audit data on boot up time
                self.game_data['Time Stamps']['Last Boot-Up'] =str(strftime("%d %b %Y %H:%M"))
                if self.game_data['Time Stamps']['First Boot-Up']=='Not Set':
                     self.game_data['Time Stamps']['First Boot-Up'] = self.game_data['Time Stamps']['Last Boot-Up']
                self.save_game_data()

                self.start_time = time.time()


#		print "Stats:"
#		print self.game_data
#		print "Settings:"
#		print self.settings
                
		self.log.info("Initial switch states:")
		for sw in self.switches:
			self.log.info("  %s:\t%s" % (sw.name, sw.state_str()))

                self.balls_per_game = self.user_settings['Standard']['Balls Per Game']
		self.setup_ball_search()
                #self.score_display.set_left_players_justify(self.user_settings['Display']['Left side score justify'])


		# Note - Game specific item:
		# The last parameter should be the name of the game's ball save lamp
		self.ball_save = procgame.modes.BallSave(self, self.lamps.shootAgain,'shooterLane' )

		trough_switchnames = []
		# Note - Game specific item:
		# This range should include the number of trough switches for
		# the specific game being run.  In range(1,x), x = last number + 1.
		for i in range(1,4):
			trough_switchnames.append('trough' + str(i))
		early_save_switchnames = ['rightOutlane', 'leftOutlane']

		#setup trough
                self.trough = Trough(game=self,drain_callback=self.drain_callback)

		# Link ball_save to trough
		self.trough.ball_save_callback = self.ball_save.launch_callback
		self.trough.num_balls_to_save = self.ball_save.get_num_balls_to_save
		self.ball_save.trough_enable_ball_save = self.trough.enable_ball_save

		# Setup and instantiate service mode
                #move all this to my own service mode class
		self.sound.register_sound('service_enter', sound_path+"menu_in.wav")
		self.sound.register_sound('service_exit', sound_path+"menu_out.wav")
		self.sound.register_sound('service_next', sound_path+"next_item.wav")
		self.sound.register_sound('service_previous', sound_path+"previous_item.wav")
		self.sound.register_sound('service_switch_edge', sound_path+"switch_edge.wav")
		self.sound.register_sound('service_save', sound_path+"save.wav")
		self.sound.register_sound('service_cancel', sound_path+"cancel.wav")

                #change this to my own version
		#self.service_mode = procgame.service.ServiceMode(self,100,font_tiny7,[])
                self.service_mode = ServiceMode(self,100,font_07x5,font_09Bx7,[])

		# Setup fonts
		self.fonts = {}
		self.fonts['tiny7'] = font_tiny7
		self.fonts['jazz18'] = font_jazz18
        	self.fonts['18x12'] = font_18x12
 		self.fonts['07x5'] = font_07x5
                self.fonts['num_14x10'] = font_14x10
		self.fonts['num_07x4'] = font_07x4
                self.fonts['num_09Bx7'] = font_09Bx7
                self.fonts['6x6_bold'] = font_6x6_bold
                self.fonts['23x12'] = font_23x12

                #setup paths
                self.paths = {}
                self.paths['game'] = game_path
                self.paths['sound'] = sound_path
                self.paths['speech'] = voice_path
                self.paths['music'] = music_path

                #register game play lamp show
#                self.lampctrl.register_show('success', game_path +"lamps/game/success.lampshow")
#                self.lampctrl.register_show('ball_lock', game_path +"lamps/game/ball_lock.lampshow")
#                self.lampctrl.register_show('hit', game_path +"lamps/game/success.lampshow")
#                self.lampctrl.register_show('jackpot', game_path +"lamps/game/success.lampshow")

                #setup high scores
		self.highscore_categories = []
		
		cat = highscore.HighScoreCategory()
                cat.game_data_key = 'ClassicHighScoreData'
		self.highscore_categories.append(cat)

                for category in self.highscore_categories:
			category.load_from_game(self)


                #setup date & time display
                self.show_date_time = self.user_settings['Standard']['Show Date and Time']

                #setup max players
                self.max_players = 4;

                #add basic modes
                #------------------
                #attract mode
		self.attract_mode = Attract(self,1)
                #basic game control mode
		self.base_game_mode = BaseGameMode(self,2)

                #device modes
                #ac_relay
                self.ac_relay = ACRelay(self,3)
                #coils mode
                self.switched_coils = SwitchedCoils(self,4)
                #tilt mode
                self.tilt = Tilt(self,5)

                #effects mode
                self.effects = Effects(self,6)
                #extra ball mode
                self.extra_ball = Extra_Ball(self,91)

                #match mode
                self.match = Match(self,10)
                
                #------------------

		# Instead of resetting everything here as well as when a user
		# initiated reset occurs, do everything in self.reset() and call it
		# now and during a user initiated reset.
		self.reset()

#        def acSelect(self,name):
#            for coil in self.coils.items_tagged('C'):
#                if name==coil.name:
#                    self.coils.acSelect.enable()
#                else:
#                    self.coils.acSelect.disable()


        def set_player_stats(self,id,value):
            p = self.current_player()
            p.player_stats[id]=value

        def get_player_stats(self,id):
            p = self.current_player()
            return p.player_stats[id]

	def reset(self):
		# Reset the entire game framework
		super(Game, self).reset()

		# Add the basic modes to the mode queue
                self.modes.add(self.ac_relay)
                self.modes.add(self.switched_coils)
		self.modes.add(self.ball_search)
                self.modes.add(self.tilt)
		self.modes.add(self.ball_save)
		self.modes.add(self.trough)
                self.modes.add(self.effects)
                self.modes.add(self.extra_ball)
                self.modes.add(self.attract_mode)
                
    
		# Make sure flippers are off, especially for user initiated resets.
		self.enable_flippers(enable=False)



	# Empty callback just incase a ball drains into the trough before another
	# drain_callback can be installed by a gameplay mode.
	def drain_callback(self):
		pass


        def start_game(self):
		super(Game, self).start_game()

                #reset the score display
                self.score_display.reset()

                #update game start audits
		self.game_data['Audits']['Games Started'] += 1
                self.game_data['Time Stamps']['Last Game Start'] =str(strftime("%d %b %Y %H:%M"))
                if self.user_settings['Standard']['Free Play'].startswith('N'):
                    self.game_data['Audits']['Credits'] -= 1
                self.save_game_data()

                
                
	def ball_starting(self):
		super(Game, self).ball_starting()
		self.modes.add(self.base_game_mode)

                #update the display
                self.score_display.update_layer()

	def ball_ended(self):
		self.modes.remove(self.base_game_mode)
		super(Game, self).ball_ended()

	def game_ended(self):
		super(Game, self).game_ended()
     
                #for mode in self.modes:
                    #self.modes.remove(mode)

                self.modes.remove(self.base_game_mode)

		#self.set_status("Game Over")
		#self.modes.add(self.attract_mode)

                self.modes.add(self.match)

                #update games played stats
                self.game_data['Audits']['Games Played'] += 1
                #save game audit data
                self.save_game_data()

        def score(self, points):
		super(Game, self).score(points)
                #update the display
                self.score_display.update_layer()

	def set_status(self, text):
		self.dmd.set_message(text, 3)
		self.log.info("Status Text:"+text)

	def extra_ball_count(self):
		p = self.current_player()
		p.extra_balls += 1
                

	def setup_ball_search(self):
		# No special handlers in starter game.
		special_handler_modes = []
		self.ball_search = procgame.modes.BallSearch(self, priority=100, \
                                     countdown_time=10, coils=self.ballsearch_coils, \
                                     reset_switches=self.ballsearch_resetSwitches, \
                                     stop_switches=self.ballsearch_stopSwitches, \
                                     special_handler_modes=special_handler_modes)


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
