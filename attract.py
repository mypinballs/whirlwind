# Attract Mode

import procgame
import locale
import logging
import audits
import time
from procgame import *
from random import *
from service import *
from time import strftime


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


#lampshow_files = [game_path +"lamps/attract_show_test.lampshow"]
lampshow_files = [game_path +"lamps/general/colours.lampshow", \
                  game_path +"lamps/general/updown.lampshow", \
                  game_path +"lamps/general/downup.lampshow", \
                  game_path +"lamps/general/leftright.lampshow", \
                  game_path +"lamps/general/rightleft.lampshow", \
                  game_path +"lamps/general/quickwindmills.lampshow", \
                  game_path +"lamps/general/windmills.lampshow", \
                  game_path +"lamps/general/rollleft.lampshow", \
                  game_path +"lamps/general/rollright.lampshow",\
                  game_path +"lamps/general/sweep_up.lampshow", \
                  game_path +"lamps/general/sweep_down.lampshow"]
                  
class Attract(game.Mode):
	"""docstring for AttractMode"""
	def __init__(self, game, priority):
		super(Attract, self).__init__(game, priority)
                self.log = logging.getLogger('whirlwind.attract')
                self.display_order = [0,1,2,3,4,5,6,7,8,9]
		self.display_index = 0
		self.game.sound.register_sound('burp', sound_path+'burp.ogg')
                self.game.sound.register_sound('power_up', speech_path+"whirlwind.ogg")
                self.game.sound.register_sound('coin', sound_path+"coin_1.ogg")

                self.game.sound.register_sound('flipperAttract', sound_path+'burp.ogg')
                self.game.sound.register_sound('flipperAttract', speech_path+"feel_the_power.ogg")
                self.game.sound.register_sound('flipperAttract', speech_path+"ooh_million.ogg")
                self.game.sound.register_sound('flipperAttract', speech_path+"whirlwind.ogg")
                self.game.sound.register_sound('flipperAttract', speech_path+"youall_come_back_now.ogg")

                self.sound_timestamp = time.time()
                self.highscore_script = []

	def mode_topmost(self):
		pass

	def mode_started(self):

                # Register lampshow files for attact
		self.lampshow_keys = []
		key_ctr = 0
		for file in lampshow_files:
                    if file.find('flasher',0)>0:
                        key = 'attract_flashers_' + str(key_ctr)
                    else:
                        key = 'attract_lamps_' + str(key_ctr)
                    self.lampshow_keys.append(key)
                    self.game.lampctrl.register_show(key, file)
                    key_ctr += 1

		# Blink the start button to notify player about starting a game.
		#self.game.lamps.start.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=False)

                # Turn on GI lamps
		self.delay(name='gi_delay', event_type=None, delay=0, handler=self.gi)

                self.log.info("attract mode after gi turn on")

                #play power up sound
                self.game.sound.play("power_up")

                # run attract feature lamp patterns
                #self.change_lampshow()
                self.schedule_all_lamps()

                #check trough status
                self.log.info("Trough is full:" +str(self.game.trough.is_full()))
                
                #check for stuck balls
                self.delay(name='stuck_balls', event_type=None, delay=2, handler=self.release_stuck_balls)
                    
                #run attract screens
                self.attract_display()

        def mode_stopped(self):
		self.game.lampctrl.stop_show()
                self.game.score_display.cancel_script()

	def mode_tick(self):
		pass


        def gi(self):
            self.game.coils.upperPlayfieldGIOff.disable()
            self.game.coils.lowerPlayfieldGIOff.disable()

        def gi_off(self):
            self.game.coils.upperPlayfieldGIOff.enable()
            self.game.coils.lowerPlayfieldGIOff.enable()

        def release_stuck_balls(self):
            #Release Stuck Balls code
            if self.game.switches.leftCellar.is_active(0.5):
               self.game.coils.cellarKickout.pulse()
               
            if self.game.switches.outhole.is_active(0.5):
               self.game.switched_coils.drive('outhole')

            if self.game.switches.topSingleDropTarget.is_active(0.5):
                self.game.switched_coils.drive('singleDropTargetReset')

            if self.game.switches.rightRampDown.is_active(0.5):
                self.game.switched_coils.drive('rampLifter')

            if self.game.switches.topRightEject.is_active(0.5):
                self.game.switched_coils.drive('topEject')

            if self.game.switches.lock1.is_active(0.5):
                self.game.switched_coils.drive('leftLockKickback')
                self.game.trough.num_balls_locked = 0

            if self.game.switches.shooterLane.is_active(0.5) and self.game.auto_launch_enabled:
                self.game.coils.autoLaunch.pulse()

            self.game.coils.spinWheelsMotor.pulse()


        def change_lampshow(self):
		shuffle(self.lampshow_keys)

                #turn gi on or off depending on lampshow chosen from shuffle
                if self.lampshow_keys[0].find('flasher',0)>0:
                    self.gi_off()
                else:
                    self.gi()

		self.game.lampctrl.play_show(self.lampshow_keys[0], repeat=True)
		self.delay(name='lampshow', event_type=None, delay=10, handler=self.change_lampshow)


        def schedule_all_lamps(self, enable=True):
		# Start the lamps doing a crazy rotating sequence:
		schedules = [0xffff0000, 0xfff0000f, 0xff0000ff, 0xf0000fff, 0x0000ffff, 0x000ffff0, 0x00ffff00, 0x0ffff000]
		for index, lamp in enumerate(sorted(self.game.lamps, key=lambda lamp: lamp.number)):
			if enable:
				sched = schedules[index%len(schedules)]
				lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
			else:
				lamp.disable()


        def attract_display(self):
#                script = list()
#
#                script.append({'seconds':5.0, 'layer':self.zidware_logo})
#                script.append({'seconds':5.0, 'layer':self.game_logo_layer})
#		script.append({'seconds':3.0, 'layer':self.pricing_layer})
#		#script.append({'seconds':5.0, 'layer':self.credits_layer})
#		#script.append({'seconds':3.0, 'layer':None})
#
#                script.append({'seconds':3.0, 'layer':self.scores_layer})
#		for frame in highscore.generate_highscore_frames(self.game.highscore_categories):
#                    new_layer = dmd.FrameLayer(frame=frame)
#                    new_layer.transition = dmd.PushTransition(direction='west')
#                    script.append({'seconds':2.0, 'layer':new_layer})
#
#                if self.game.user_settings['Standard']['Show Date and Time'].startswith('Y'):
#                    script.append({'seconds':10.0, 'layer':self.date_time_layer})
#
#                #add in the game over screen

#
#		self.layer = dmd.ScriptedLayer(width=128, height=32, script=script)
                #self.layer = dmd.ScriptedLayer(128, 32, [{'seconds':10.0, 'layer':self.mypinballs_logo}, {'seconds':2.0, 'layer':self.press_start}, {'seconds':2.0, 'layer':None}])
                #self.game.set_status("V1.0")




                self.log.info("setting attract slides")
                #debug
                #self.game.score_display.set_text('whirlwind'.upper(),0,'center',seconds=5)
                #self.game.score_display.set_transition_in('whirlwind'.upper(),0,seconds=5)
                #self.game.score_display.set_text('*mypinballs v1.0'.upper(),1,'center',seconds=5)

                script=[]

                #logo
                #self.mypinballs_logo.transition = dmd.ExpandTransition(direction='horizontal')
                script.append({'top':'mypinballs'.upper(),'bottom':'','timer':5,'transition':0})

                #system stuff
                #self.game_logo_layer.transition = dmd.PushTransition(direction='north')
                script.append({'top':self.game.system_name.upper(),'bottom':'V'+self.game.system_version.upper(),'timer':5,'transition':3})

                #pricing
                self.update_pricing()
                script.append({'top':self.pricing_top.upper(),'bottom':self.pricing_bottom.upper(),'timer':5,'transition':4})

                #replays
                replay_type =self.game.user_settings['Replay']['Replay Award'] +" AT"
                replay_levels = int(self.game.user_settings['Replay']['Replay Levels'])
                
                for i in range(replay_levels):
                    name = 'Replay Level '+str(i+1)
                    script.append({'top':replay_type.upper(),'bottom':locale.format("%d", self.game.user_settings['Replay'][name], True),'timer':4,'transition':2})

                #high scores
                for category in self.game.highscore_categories:
                    for index, score in enumerate(category.scores):
			score_str = locale.format("%d", score.score, True)
			ranking = str(index)
                        name = str(score.inits)

                        if category.game_data_key =='ClassicHighScoreData':
                            data={'score':score_str, 'ranking':ranking}
                            if index==0:
                                text1 = 'champion ('+name+')'
                                text2 = score_str
                            else:
                                text1 = 'high score '+ranking+')'
                                text2 = name+' '+score_str

                        else:
                            text1 = category.titles[0]
                            text2 = locale.format("%d", score.score, True)+" "+category.score_suffix_plural

                        script.append({'top':text1.upper(),'bottom':text2.upper(),'timer':5,'transition':1})

                #date and time
                #self.date_time_layer.transition = dmd.PushTransition(direction='west')
                if self.game.user_settings['Standard']['Show Date and Time'].startswith('Y'):
                    day = str(strftime("%A"))
                    date= str(strftime("%d %b %Y"))
                   
                    script.append({'top':day.upper(),'bottom':date.upper(),'timer':5,'transition':3})

                #game over text
                index=3
                time=3
                if self.game.system_status=='game_over':
                    index=0
                    time=10
                    self.game.system_status='attract'
                #self.game_over_layer.transition = dmd.CrossFadeTransition(width=128,height=32)
                script.insert(index,{'top':'game over'.upper(),'bottom':'','timer':time,'transition':0})


                #set the script for the display to run
                self.game.score_display.set_script(script)


#        def highscores(self,categories):
#            i=0
#            interval = 10
#            posn=0
#            for category in categories:
#                for index, score in enumerate(category.scores):
#			score_str = str(score.score)
#			ranking = str(index+1)
#
#                        data={'score':score_str, 'ranking':ranking}
#                        text = '<'+ranking+'> '+store_str
#
#                        self.delay(name='highscore_rankings',event_type=None, delay=i,handler=lambda: self.game.score_display.set_transition_in(text,0,seconds=5))
#                        posn+=1
#                        if posn>1:
#                            posn=0
#                            i+=interval
            
        def update_pricing(self):
            self.pricing_top = ''
            self.pricing_bottom = ''

            if self.game.user_settings['Standard']['Free Play'].startswith('Y'):
                self.pricing_top='FREE PLAY'
            else:
                self.pricing_top=str(audits.display(self.game,'general','creditsCounter')+" CREDITS")

            if audits.display(self.game,'general','creditsCounter') >0 or self.game.user_settings['Standard']['Free Play'].startswith('Y'):
                self.pricing_bottom = 'PRESS START'
            else:
                self.pricing_bottom = 'INSERT COINS'

            

        def show_pricing(self):
            self.update_pricing()

            self.game.score_display.set_text(self.pricing_top,0,'center',seconds=5)
            self.game.score_display.set_text(self.pricing_bottom,1,'center',seconds=5)

#            bgnd_anim = "dmd/blank.dmd"
#            anim = dmd.Animation().load(game_path+bgnd_anim)
#            bgnd_layer = dmd.AnimatedLayer(frames=anim.frames, opaque=False, repeat=False, hold=False, frame_time=3)
#            bgnd_layer.add_frame_listener(-1, self.attract_display)
#            self.layer  = dmd.GroupedLayer(128, 32, [bgnd_layer,self.pricing_layer])


        def sound_effects(self):
             if time.time()-self.sound_timestamp>5:
                self.game.sound.play_voice('flipperAttract')
                self.sound_timestamp=time.time()

	# Enter service mode when the enter button is pushed.
	def sw_enter_active(self, sw):
		for lamp in self.game.lamps:
			lamp.disable()

                #self.service_mode = ServiceMode(self,100,font_07x5,[])
		self.game.modes.add(self.game.service_mode)
		return True

	def sw_exit_active(self, sw):
		return True

	# Outside of the service mode, up/down control audio volume.
	def sw_down_active(self, sw):
		volume = self.game.sound.volume_down()
		self.game.set_status("Volume Down : " + str(volume))
		return True

	def sw_up_active(self, sw):
		volume = self.game.sound.volume_up()
		self.game.set_status("Volume Up : " + str(volume))
		return True

	# Start button starts a game if the trough is full.  Otherwise it
	# initiates a ball search.
	# This is probably a good place to add logic to detect completely lost balls.
	# Perhaps if the trough isn't full after a few ball search attempts, it logs a ball
	# as lost?
	def sw_start_active(self, sw):
            if self.game.user_settings['Standard']['Free Play'].startswith('Y') or audits.display(self.game,'general','creditsCounter') >0:
		if self.game.trough.is_full():
			# Remove attract mode from mode queue
			self.game.modes.remove(self)
			# Initialize game
                        if self.game.switches.flipperLwR.is_active(0.5):
                            self.game.start_game(force_moonlight=True)
                        else:
                            self.game.start_game(force_moonlight=False)
                        
			# Add the first player
			self.game.add_player()
			# Start the ball.  This includes ejecting a ball from the trough.
			self.game.start_ball()
                        

                        #sounds for first player start
                        self.game.sound.play_voice('uhoh_rain')
                        #set the gi
                        self.game.coils.upperPlayfieldGIOff.enable()
                        #self.game.coils.lowerPlayfieldGIOff.disable()
		else:
                        self.game.score_display.cancel_script()
                        time = 5
			self.game.score_display.set_text("LOOKING",0,'center',seconds=time)
                        self.game.score_display.set_text("FOR BALLS",1,'center',seconds=time)
			self.game.ball_search.perform_search(time)
                        self.delay(name='restart_attract_display', event_type=None, delay=time, handler=self.attract_display)
                        
		
            else:
                self.show_pricing()

            return True


        def sw_coin_active(self, sw):
            self.credits =  audits.display(self.game,'general','creditsCounter')
            audits.update_counter(self.game,'credits',self.credits+1)
            self.show_pricing()
            self.game.sound.play("coin")


        def sw_flipperLwL_active(self, sw):
                self.sound_effects()

        def sw_flipperLwR_active(self, sw):
                self.sound_effects()