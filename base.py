import procgame
import locale
import random
import logging
import time
from procgame import *
from bonus import *
from pops import *
from tornado import *
from skyway import *
from cellar import *
from ramp import *
from compass import *
from multiball import *
from skillshot import *
from drops import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

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
                self.game.sound.register_sound('uhoh_rain', speech_path+"uhoh_rain.ogg")
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
                self.game.sound.register_sound('ball_save_speech', speech_path+"well_lucky_here.ogg")
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