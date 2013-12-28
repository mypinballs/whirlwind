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
import random
import logging

from ac_relay import *
from switched_coils import *
from scoredisplay import *
from effects import *
from extra_ball import *
from service import *
from attract import *
from bonus import *
from tilt import *
from match import *
from pops import *
from tornado import *
from skyway import *
from cellar import *
from ramp import *
from compass import *
from multiball import *
from skillshot import *
from drops import *
from trough import *
from procgame import *
from threading import Thread
from random import *
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



class BaseGameMode(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game,priority):
		super(BaseGameMode, self).__init__(game, priority)

                self.log = logging.getLogger('whirlwind.base')

                self.tilt_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)
		self.layer = None # Presently used for tilt layer
		self.ball_starting = True

                #register music files
                self.game.sound.register_music('shooter', music_path+"shooter.aiff")
                self.game.sound.register_music('general_play', music_path+"general_play.ogg")
                self.game.sound.register_music('end', music_path+"general_play_end.ogg")

                #register sound/speech call files
                self.game.sound.register_sound('uhoh_rain', voice_path+"uhoh_rain.ogg")
                self.game.sound.register_sound('start', sound_path+"coin_in.ogg")
                self.game.sound.register_sound('slingshot', sound_path+"sling_1.ogg")
                self.game.sound.register_sound('rebound', sound_path+"sling_2.ogg")
                #self.game.sound.register_sound('slingshot', sound_path+"sling_3.ogg")
                #self.game.sound.register_sound('slingshot', sound_path+"sling_4.ogg")
                self.game.sound.register_sound('left_inlane', sound_path+"inlane_1.ogg")
                self.game.sound.register_sound('right_inlane', sound_path+"inlane_2.ogg")
                #self.game.sound.register_sound('inlane', sound_path+"inlane_3.ogg")
                #self.game.sound.register_sound('inlane', sound_path+"inlane_4.ogg")
                self.game.sound.register_sound('outlane', sound_path+"outlane_1.ogg")
                #self.game.sound.register_sound('outlane', sound_path+"outlane_2.ogg")
                self.game.sound.register_sound('ball_launch', sound_path+"ball_launch.ogg")
                self.game.sound.register_sound('ball_save', sound_path+"ball_save.ogg")
                self.game.sound.register_sound('ball_save_speech', voice_path+"well_lucky_here.ogg")
                self.game.sound.register_sound('big_thunder', sound_path+"thunder_crack.ogg")
                self.ball_saved = False



	def mode_started(self):

                #debug
                self.log.info("Basic Game Mode Started, Ball "+str(self.game.ball))
              
                self.inlanes_made = self.game.get_player_stats('inlanes_made')
                
                #set player status
                self.game.set_player_stats('status','general')
                self.game.set_player_stats('ball_start_time',time.time())
                
		#Disable any previously active lamp
		for lamp in self.game.lamps:
			lamp.disable()

		# Turn on the GIs
		# Some games don't have controllable GI's (ie Stern games)
#		self.game.lamps.gi01.pulse(0)
#		self.game.lamps.gi02.pulse(0)
#		self.game.lamps.gi03.pulse(0)
#		self.game.lamps.gi04.pulse(0)

		# Enable the flippers
                #print "Game Config: "+str(self.game.config)
		self.game.enable_flippers(True)

                # Each time this mode is added to game Q, set this flag true.
		self.ball_starting = True

                #setup basic modes
                self.add_basic_modes(self);

		# Put the ball into play and start tracking it.
		self.game.trough.launch_balls(1, self.ball_launch_callback)

                # Enable ball search in case a ball gets stuck during gameplay.
		self.game.ball_search.enable()

		# Reset tilt
                self.game.tilt.reset()

		# In case a higher priority mode doesn't install it's own ball_drained
		# handler.
		self.game.trough.drain_callback = self.ball_drained_callback		

                #ball save callback - exp
                self.game.ball_save.callback = self.ball_save_callback

                self.start_effects()

                #Update lamp status's for all modes
                self.game.update_lamps()
                
        def start_effects(self):
            #sounds &effects for first player start
            if len(self.game.players)==1 and self.game.ball==1:
                voice_delay = self.game.sound.play_voice('uhoh_rain')
                self.delay(delay=voice_delay+0.1,handler=lambda:thunder_effect())
                self.delay(delay=voice_delay+0.3,handler=lambda:thunder_effect2())
                self.delay(delay=voice_delay+0.5,handler=lambda:thunder_effect3())

                def thunder_effect():
                    self.game.sound.play('big_thunder')
                    self.game.effects.drive_flasher('lightningLeftFlasher',style='fast',time=0.5)
                def thunder_effect2():
                    self.game.effects.drive_flasher('lightningMiddleFlasher',style='fast',time=0.3)
                def thunder_effect3():
                    self.game.effects.drive_flasher('lightningRightFlasher',style='fast',time=0.3)

                #delay to turn upper gi back on
                gi_on_delay = self.game.sound.play_voice('big_thunder')
                self.delay(delay=gi_on_delay,handler=self.game.coils.upperPlayfieldGIOff.disable)



        def add_basic_modes(self,ball_in_play):

            #lower priority basic modes
            self.pops = Pops(self.game, 40)
            self.drops = Drops(self.game,41)
            self.tornado = Tornado(self.game,41)
            self.skyway = Skyway(self.game,42,self.tornado)
            self.cellar = Cellar(self.game,43)
            self.ramp = Ramp(self.game,44,self.skyway,self.cellar)



            #medium priority basic modes
            self.multiball = Multiball(self.game,50)
            self.compass = Compass(self.game,51,self.multiball)
            self.skillshot = Skillshot(self.game, 52)

            #higher priority basic modes

            

            #start modes
            self.game.modes.add(self.pops)
            self.game.modes.add(self.drops)
            self.game.modes.add(self.tornado)
            self.game.modes.add(self.skyway)
            self.game.modes.add(self.cellar)
            self.game.modes.add(self.ramp)
            self.game.modes.add(self.compass)
            self.game.modes.add(self.skillshot)
            


        def ball_save_callback(self):
            #anim = dmd.Animation().load(game_path+"dmd/eternal_life.dmd")
            #self.layer = dmd.AnimatedLayer(frames=anim.frames,hold=False)
            self.game.sound.play_voice('ball_save_speech')
            #self.game.sound.play('ball_save')

            self.ball_saved = True


	def ball_launch_callback(self):
            #print("Debug - Ball Starting var is:"+str(self.ball_starting))
            if self.ball_starting:
                #print("Debug - Starting Ball Save Lamp")
                #self.game.ball_save.start_lamp()
                
                #start shooter lane music
                self.game.sound.play_music('shooter', loops=-1)

        def score(self, points):
		super(BaseGameMode, self).score(points)
		#EventManager.default().post(name=events.SCORE_CHANGED, object=self)
                pass

        def mode_tick(self):
            if self.game.switches.start.is_active(1) and self.game.switches.flipperLwL.is_active(1) and self.game.switches.flipperLwR.is_active():
                print("reset button code entered")
                self.game.sound.stop_music()
                self.game.end_run_loop()

		while len(self.game.dmd.frame_handlers) > 0:
                    del self.game.dmd.frame_handlers[0]
                    
		del self.game.proc

	def mode_stopped(self):

                self.log.info("Basic Game Mode Ended, Ball "+str(self.game.ball))

		# Ensure flippers are disabled
		self.game.enable_flippers(enable=False)

		# Deactivate the ball search logic so it won't search due to no
		# switches being hit.
		self.game.ball_search.disable()

                #remove modes
                self.game.modes.remove(self.pops)
                self.game.modes.remove(self.skyway)
                self.game.modes.remove(self.cellar)
                self.game.modes.remove(self.drops)
                self.game.modes.remove(self.tornado)
                self.game.modes.remove(self.ramp)
                self.game.modes.remove(self.compass)

                #update audits
                self.update_game_audits()


        def update_game_audits(self):
                #update the game audits
                current_ball_time =  int(time.time())-self.game.get_player_stats('ball_start_time')
                current_on_time  = int(time.time())-self.game.start_time

                self.game.game_data['Audits']['Balls Played'] += 1
                self.game.game_data['Time Stamps']['Overall Game Time']+= current_ball_time
                self.game.game_data['Time Stamps']['Overall Time On'] += current_on_time
                self.game.game_data['Audits']['Average Ball Time'] = self.game.game_data['Time Stamps']['Overall Game Time']/self.game.game_data['Audits']['Balls Played']
                if self.game.game_data['Audits']['Games Played']>=1:
                    self.game.game_data['Audits']['Average Game Time'] = self.game.game_data['Time Stamps']['Overall Game Time']/self.game.game_data['Audits']['Games Played']

                player = self.game.current_player()
                self.game.game_data['Hidden']['Total Score']+=player.score
                if self.game.game_data['Audits']['Games Played']>=1:
                    self.game.game_data['Audits']['Average Score'] =self.game.game_data['Hidden']['Total Score']/self.game.game_data['Audits']['Games Played']

                #save game audit data
                self.game.save_game_data()

                

	def ball_drained_callback(self):
		if self.game.trough.num_balls_in_play == 0:
                    # End the ball
                    self.finish_ball()

	def finish_ball(self):

                #music fadeout
                #self.game.sound.fadeout_music()

                # Create the bonus mode so bonus can be calculated.
		self.bonus = Bonus(self.game, 98)
		self.game.modes.add(self.bonus)

		# Only compute bonus if it wasn't tilted away. 23/02/2011
		if not self.game.tilt.status:
                    self.bonus.calculate(self.end_ball)
		else:
                    self.end_ball()
                    self.layer = None

		# Turn off tilt display (if it was on) now that the ball has drained.
		#if self.game.tilt.status and self.layer == self.tilt_layer:
                 #   self.layer = None

		#self.end_ball()

	def end_ball(self):
                #remove bonus mode
                self.game.modes.remove(self.bonus)
                
		# Tell the game object it can process the end of ball
		# (to end player's turn or shoot again)
		self.game.end_ball()

        
        def sw_outhole_active(self,sw):
                self.game.sound.stop_music();
                self.game.sound.play_music('end',loops=0)
                


	def sw_start_active(self, sw):
                #adding multiple players to game
		if self.game.ball == 1 and len(self.game.players)<self.game.max_players:
			p = self.game.add_player()
                        self.game.sound.play('start')
			self.log.info(p.name + " added!")

                        #update the score display
                        self.game.score_display.update_layer()

        def sw_start_active_for_2s(self, sw):
		if self.game.ball > 1 and self.game.user_settings['Standard']['Game Restart']:
			self.log.info("User initiated reset!")

			# Need to build a mechanism to reset AND restart the game.  If one ball
			# is already in play, the game can restart without plunging another ball.
			# It would skip the skill shot too (if one exists).

			# Currently just reset the game.  This forces the ball(s) to drain and
			# the game goes to AttractMode.  This makes it painfully slow to restart,
			# but it's better than nothing.
			self.game.reset()
			return True


	def sw_shooterLane_open_for_1s(self,sw):
		if self.ball_starting:
			self.ball_starting = False
			ball_save_time = 10
			self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)
		#else:
		#	self.game.ball_save.disable()

#        def sw_shooterLane_open_for_750ms(self,sw): - disabled as skillshot end start main tune now
#                #possibly change this to detect points scored?
#                #stop shooter grove and play main play music
#                self.game.sound.stop_music()
#                self.game.sound.play_music('general_play', loops=-1)

        def sw_shooterLane_open_for_250ms(self,sw):
                self.game.sound.play('ball_launch')

#        def sw_shooterLane_active_for_500ms(self,sw):
#                if self.ball_saved:
#                    self.game.coils.xxx.pulse()
#                    self.ball_saved = False

	# Note: Game specific item
	# Set the switch name to the launch button on your game.
	# If manual plunger, remove the whole section.
#	def sw_autoLaunch_active(self, sw):
#		if self.game.switches.shooter.is_active():
#			self.game.coils.ballLaunch.pulse(50)
#                        self.game.coils.flasherRightSide.schedule(0x00003333, cycle_seconds=1.5, now=True)
#                        self.game.sound.play("gun_shot")
#                if self.game.switches.flipperLwL.is_active() and self.ball_starting:
#                        self.game.modes.add(self.skillshot)

        #skillshot preview
#        def sw_flipperLwL_active_for_500ms(self, sw):
#            if self.ball_starting and self.game.switches.shooter.is_active():
#                self.skillshot.activate_lamps()
#
#        #skillshot preview
#        def sw_flipperLwL_inactive(self, sw):
#            if self.ball_starting and self.game.switches.shooter.is_active():
#                self.skillshot.clear_lamps()


	# Allow service mode to be entered during a game.
	def sw_enter_active(self, sw):
		self.game.modes.add(self.game.service_mode)
		return True	
			

        def sw_leftRebound_active(self,sw):
            self.rebound()

        def sw_rightRebound_active(self,sw):
            self.rebound()
                        
        def sw_leftSlingshot_active(self,sw):
            self.sling()

        def sw_rightSlingshot_active(self,sw):
            self.sling()

        def sw_leftInlane_active(self,sw):
            self.inlane('left')
            self.game.game_data['Audits']['Left Inlanes'] += 1

        def sw_rightInlane_active(self,sw):
            self.inlane('right')
            self.game.game_data['Audits']['Right Inlanes'] += 1

        def sw_rightOutlane_active(self,sw):
            self.outlane()
            self.game.game_data['Audits']['Right Outlane Drains'] += 1
            
        def sw_leftOutlane_active(self,sw):
            self.outlane()
            self.game.game_data['Audits']['Left Outlane Drains'] += 1

        def rebound(self):
            self.game.score(110)
            self.game.sound.play('rebound')

        def sling(self):
            self.game.score(10)
            self.game.sound.play('slingshot')

        def inlane(self,name):
            self.game.score(100)
            self.game.sound.play(name+"_inlane")
            self.inlanes_made+=1
            self.game.set_player_stats('inlanes_made',self.inlanes_made)

        def outlane(self):
            self.game.score(200)
            self.game.sound.play("outlane")


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
		return mpcPlayer(name)
                

	def setup(self):
		"""docstring for setup"""
		self.load_config(self.yamlpath)

                self.load_settings(settings_template_path, settings_path)
		self.sound.music_volume_offset = self.user_settings['Sound']['Music volume offset']
		self.sound.set_volume(self.user_settings['Sound']['Initial volume'])
		self.load_game_data(game_data_template_path, game_data_path)

                #define system status var
                self.system_status='power_up'
                self.system_version='0.1.11'
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


class mpcPlayer(game.Player):

	def __init__(self, name):
		super(mpcPlayer, self).__init__(name)

                #create player stats
                self.player_stats = {}

                #set player stats defaults
                self.player_stats['status']=''
                self.player_stats['bonus_x']=1
                self.player_stats['skyway_tolls']=1
                self.player_stats['cellar_visits']=0
                self.player_stats['pop_flags']=[0,0,0,0,0,0]
                self.player_stats['lower_super_pops_collected']=0
                self.player_stats['lower_super_pops_level']=0
                self.player_stats['upper_super_pops_collected']=0
                self.player_stats['upper_super_pops_level']=0
                self.player_stats['tornado_level']=0
                self.player_stats['tornados_collected']=0
                self.player_stats['saucers_collected']=0
                self.player_stats['ramps_made']=0
                self.player_stats['compass_flags']=[0,0,0,0,0,0,0,0]
                self.player_stats['compass_level']=1
                self.player_stats['compass_sets_complete']=0
                self.player_stats['letters_collected']=0
                self.player_stats['inlanes_made']=0
                self.player_stats['lock_lit']=False
                self.player_stats['multiball_ready']=False
                self.player_stats['multiball_started']=False
                self.player_stats['balls_locked']=0
                self.player_stats['million_lit']=False
                self.player_stats['ball_start_time']=0
                self.player_stats['drop_banks_completed']=0
                self.player_stats['skillshot_level']=1
                self.player_stats['skillshot_in_progress']=False
                


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
