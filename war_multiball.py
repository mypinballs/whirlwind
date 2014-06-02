#War Multiball
#Secret Mode
#Homage to Black Knight 2000

import procgame
import locale
import random
import logging
import audits
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class WarMultiball(game.Mode):

	def __init__(self, game, priority):
            super(WarMultiball, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.war_multiball')

            self.game.sound.register_music('lock_lit', music_path+"lock_lit.ogg")
            self.game.sound.register_music('end', music_path+"lock_lit_end.ogg")
            self.game.sound.register_music('war_multiball_play', music_path+"war_multiball_play.aiff")
            self.game.sound.register_music('war_multiball_intro', music_path+"war_multiball_intro.aiff")

            self.game.sound.register_sound('war_lane_lit', sound_path+"war_lane_lit.aiff")
            self.game.sound.register_sound('war_lane_unlit', sound_path+"war_lane_unlit.aiff")
            self.game.sound.register_sound('war_lane_fanfare', sound_path+"war_lane_fanfare.aiff")
            self.game.sound.register_sound('war_ball_locked', sound_path+"war_ball_locked.aiff")
            self.game.sound.register_sound('war_mb_start', sound_path+"war_mb_start.aiff")

            self.game.sound.register_sound('bk_announce', speech_path+"bk_announce.aiff")
            self.game.sound.register_sound('bk_laugh', speech_path+"bk_laugh.aiff")
            self.game.sound.register_sound('bk_fight', speech_path+"bk_fight.aiff")

            self.flashers = ['rampBottomFlasher','rampLMFlasher','rampUMFlasher','rampTopFlasher','spinnerFlasher','bottomRightFlasher']
            self.lightning_flashers = ['lightningLeftFlasher','lightningMiddleFlasher','lightningRightFlasher']

           
            self.lamps = ['middleStandup','nwTop','neTop']

            self.enter_value = 10
            self.made_value_base = 50000
            self.made_value_boost = 10000
            self.made_value_max = 100000
            self.skyway_toll_boost = 3
            self.super_combo_multiplier = 10
            self.combo_multiplier = 2
            self.million_value = 1000000
            self.million_timer = 30 #change to setting

            self.lane_unlit_value = 5000
            self.lane_lit_value = 1000

            self.balls_needed = 2
            self.next_ball_ready = False
            self.virtual_lock = False
            self.multiball_info_text_flag = 0
            self.end_callback= None

            
        
        def reset(self):
            self.reset_combos()
            self.letters_spotted = 0
            self.lane_flag = [False,False,False]

        def reset_combos(self):
            self.combo = False
            self.super_combo = False

        
#        def update_lamps(self):
#            for i in range(self.lamps):
#                self.game.effects.drive_lamp(self.lamps[i],'on')
#
        def update_lamps(self):
            self.log.info("Updating WAR lane Lamps")
            for i in range(len(self.lamps)):
                if self.lane_flag[i]:
                    self.game.effects.drive_lamp(self.lamps[i],'on')
                else:
                    self.game.effects.drive_lamp(self.lamps[i],'off')

        def set_lamps_help(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'superfast')

        def completed_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'superfast')


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')


        def compass_lamps(self, enable=True):
            # Start the lamps doing a crazy rotating sequence:
            schedules = [0xffff000f, 0xfff000ff, 0xff000fff, 0xf000ffff, 0x000fffff, 0x00fffff0, 0x0fffff00, 0xfffff000]
            for index, lamp in enumerate(sorted(self.game.lamps.items_tagged('compass'), key=lambda lamp: lamp.number)):
                if enable:
                    sched = schedules[index%len(schedules)]
                    lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
                else:
                    lamp.disable()

            
        def mode_started(self):
            self.shots_made = 0
            self.lock_lit=False
            self.multiball_ready = self.game.get_player_stats('war_multiball_ready')
            self.multiball_started = self.game.get_player_stats('war_multiball_started')
            self.multiball_running = self.game.get_player_stats('war_multiball_running')

            self.reset()
            
        def mode_stopped(self):
            self.lock_lit=False
            self.multiball_ready = False
            self.game.set_player_stats('war_lock_lit',self.lock_lit)
            self.game.set_player_stats('war_multiball_ready',self.multiball_ready)


        def mode_tick(self):
            if self.multiball_started:
                self.balls_in_play = self.game.trough.num_balls_in_play

                #debug
                #self.balls_in_play=3
                #-------------------------------------------
                #debug_ball_data = str(self.balls_in_play)+":"+str(self.game.trough.num_balls())+":"+str(self.game.trough.num_balls_locked)+":"+str(self.game.trough.num_balls_to_launch)+":"+str(self.multiball_running)
                #self.game.set_status(debug_ball_data)
                #self.game.score_display.set_text(debug_ball_data.upper(),1,'left')
                #self.log.debug(debug_ball_data)
                #-------------------------------------------

                if self.balls_in_play==self.balls_needed and self.multiball_running==False:
                    #start tracking
                    self.multiball_running = True;
                    self.game.set_player_stats('quick_multiball_running',self.multiball_running)


                if self.multiball_running:
                    self.multiball_tracking()


        def million_speech(self,enable=True):
            if enable:
                self.game.sound.play_voice('million_speech')
                self.delay('million_speech_repeat',delay=10,handler=self.million_speech)
            else:
                self.cancel_delayed('million_speech_repeat')


        #this is called by other modes to start the qm process
        def lock_ready(self):
            self.lock_lit=True
            self.game.set_player_stats('war_lock_lit',self.lock_lit)

            self.display(top='WAR Multiball',bottom='Is Lit',seconds=5)

            self.game.sound.stop_music()
            self.game.sound.play_music('lock_lit',-1)
            self.delay(name='lock_lit_announce',delay=1,handler=lambda:self.game.sound.play_voice('bk_announce'))

            self.game.effects.drive_lamp('lock','fast')

            #lift ramp with delay
            self.delay(name='lift_ramp_delay',delay=0.5,handler=lambda:self.game.switched_coils.drive('rampLifter'))
           

        def ball_locked(self):

            self.display(top='WAR Multiball',bottom='Ready',seconds=3)

            #set multiball ready flag
            self.multiball_ready = True
            self.game.set_player_stats('war_multiball_ready',self.multiball_ready)
            self.log.info('War Multiball Ready')

            #update lock lit flag
            self.lock_lit=False
            self.game.set_player_stats('war_lock_lit',self.lock_lit)

            self.game.sound.play_voice('bk_laugh')
            
            #flasher effect
            self.lock_flashers()

            #cancel lock lamp
            self.game.effects.drive_lamp('lock','off')


            #queue the next ball launch
            self.delay(name='launch_next_ball',delay=0.5,handler=self.launch_next_ball)


            audits.record_value(self.game,'ballLocked')



        def launch_next_ball(self):
            if not self.virtual_lock: #skyway should handle the eject saucer with corect delay if virtual lock
                self.game.trough.launch_balls(1,stealth=False) #stealth false, bip +1
            self.next_ball_ready = True
            self.virtual_lock = False
            self.game.ball_save.start(time=10)


        def display(self, top, bottom, seconds, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_transition_reveal(text=top.upper(),row=0,seconds=seconds)
            self.game.score_display.set_transition_reveal(text=bottom.upper(),row=1,seconds=seconds)

        
        def display_lock_ready_text(self,time=3):
           self.display(top='War Multiball',bottom='Is Lit',seconds=time)


        def display_million_text(self,time=2):
            self.display(top='1 Million',bottom='Million',seconds=time)


        def display_multiball_info(self,time=3):
            if self.multiball_info_text_flag%2==0:
                self.display(top='Double Knights ',bottom='War = Million',seconds=time)
            else:
                self.display(top='Black Knight',bottom='2000 Homage',seconds=time)

            if self.multiball_info_text_flag<10:
                self.multiball_info_text_flag+=1
                self.delay(name='display_multiball_info_repeat',delay=time,handler=self.display_multiball_info,param=time)
            else:
                self.multiball_info_text_flag = 0
                self.cancel_delayed('display_multiball_info_repeat')

            

        def strobe_flashers(self,time=0.1):
            timer = 0
            repeats = 4

            #lightning flashers
            #self.game.effects.strobe_flasher_set(self.lightning_flashers,time=time,overlap=0.2,repeats=repeats)

            #playfield flashers
            sequence=[]
            for j in range(repeats):
                sequence += self.flashers

            for i in range(len(sequence)):

                def flash(i,time,delay):
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='fast',time=time+0.1))

                flash(i,time,timer)
                timer+=time


        def lock_flashers(self,time=0.1):
            timer = 0
            sequence = []

            #playfield flashers
            flashers = self.flashers
            sequence+=flashers
            flashers.reverse()
            sequence+flashers

            for i in range(len(sequence)):

                def flash(i,time,delay):
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='fast',time=time+0.1))

                flash(i,time,timer)
                timer+=time


        def multiball_start(self):
            self.log.debug('multiball start reached')

            #update the flag
            self.multiball_started = True
            self.game.set_player_stats('war_multiball_started',self.multiball_started)

            #display help info
            self.display_multiball_info(3)

            #start lamp and flasher effects
            self.multiball_effects()

            #play speech
            length = self.game.sound.play('war_ball_locked')
            self.delay(delay=length, handler=lambda:self.game.sound.play('war_mb_start'))
            
            #change music
            self.game.sound.stop_music()
            music_intro_length = self.game.sound.play_voice('war_multiball_intro')

            self.delay(name='multiball_music_delay',delay=music_intro_length, handler=lambda:self.game.sound.play_music('war_multiball_play',-1))
            self.delay(name='multiball_eject_delay',delay=3, handler=self.multiball_eject)

            #ramp down
            self.game.coils['rampDown'].pulse()

            audits.record_value(self.game,'warMultiballStarted')


        def multiball_eject(self):
            self.log.debug('multiball eject reached')

            #make sure ramp is up
            self.game.switched_coils.drive('rampLifter')

            #kick out ball
            self.game.switched_coils.drive('topEject')

            #speech
            self.game.sound.play_voice('bk_fight')

            #update trough tracking
            #self.game.trough.num_balls_locked = 0
            #self.balls_locked = 0
            self.game.trough.num_balls_in_play+=1

            #queue multiball effects
            self.delay(name='multiball_effects_delay',delay=0.5, handler=self.multiball_effects)


        def multiball_effects(self):
            #disable all regular lamps
            for lamp in self.game.lamps:
		lamp.disable()

            #set mode lamps
            self.set_lamps_help()
            self.compass_lamps()

            #run flasher effects
            self.strobe_flashers()

            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=2,allow_multiple_saves=True,time=10)


        def multiball_tracking(self):
            #end check
            if self.balls_in_play==1:
                #end tracking & update player stats
                self.multiball_running=False
                self.multiball_started = False
                self.multiball_ready = False
                
                self.game.set_player_stats('war_multiball_running',self.multiball_running)
                self.game.set_player_stats('war_multiball_started',self.multiball_started)
                self.game.set_player_stats('war_multiball_ready',self.multiball_ready)
               
                #disable all lamps
                for lamp in self.game.lamps:
                    lamp.disable()

                self.compass_lamps(False)
                #restore lamp states from other modes
                self.game.update_lamps()

                #change music
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play', loops=-1)

                #mulitball ended callback
                if self.end_callback:
                    self.log.debug('War Multiball End Callback Called')
                    self.end_callback()
           


        def award_million(self):

            #update display
            self.display_million_text()

            #set lamps
            self.completed_lamps()
            
            #update score
            self.game.score(self.million_value)

            #fanfare
            self.game.sound.play('war_lane_fanfare')

            #flashers
            self.strobe_flashers()

            #queue the reset of lamps
            self.delay(name='multiball_award_reset',delay=1, handler=self.award_reset)

            #update audits
            audits.record_value(self.game,'warMillionCollected')

        def award_reset(self):
            self.reset()
            self.reset_lamps()

            self.delay(delay=3,handler=self.set_lamps_help)


        def eject(self):
            self.game.switched_coils.drive('topEject')


        def progress(self,id):
            self.update_lamps()

            if self.lane_flag[id] == False:

                self.letters_spotted +=1
                self.lane_flag[id]=True;
                #update player stats var
                self.game.set_player_stats('war_lanes_flag',self.lane_flag)
                #print("indy lamp lit: %s "%(self.lamps[id]))
                self.game.score(self.lane_unlit_value)

                #play sounds
                if self.letters_spotted ==3:
                    self.award_million()
                else:
                    self.game.sound.play('war_lane_unlit')
                    self.game.effects.drive_lamp(self.lamps[id],'smarton')

            else:
                self.game.score(self.lane_lit_value)
                #play sounds
                self.game.sound.play('war_lane_lit')

            print(self.lane_flag)
            print(self.letters_spotted)


        def lane_change(self,direction):
            list = ['middleStandup','nwTop','neTop']
            flag_orig = self.lane_flag #[self.indyI_lit,self.indyN_lit,self.indyD_lit,self.indyY_lit]
            flag_new = [False,False,False] #[self.indyI_lit,self.indyN_lit,self.indyD_lit,self.indyY_lit]
            carry = False
            j=0

            if direction=='left':
                start = 0
                end = len(list)
                inc =1
            elif direction=='right':
                start = len(list)-1
                end = -1
                inc =-1

            for i in range(start,end,inc):
                if flag_orig[i]:

                    if direction=='left':
                        j=i-1
                        if j<0:
                            j=2
                            carry = True
                    elif direction=='right':
                        j=i+1
                        if j>2:
                            j=0
                            carry = True

                    flag_new[i] = False
                    flag_new[j]= True

                    #self.game.effects.drive_lamp(list[i],'off')
                    #self.game.effects.drive_lamp(list[j],'on')

            #update the carry index if required
            if carry:
                if direction=='left':
                    flag_new[2]= True
                    #self.game.effects.drive_lamp(list[3],'on')
                elif direction=='right':
                    flag_new[0]= True
                    #self.game.effects.drive_lamp(list[0],'on')

            #update main var
            self.lane_flag=flag_new
            #update lamps
            self.update_lamps()
            #debug log
            self.log.info('New Lane order is:%s',self.lane_flag)




        #switch handlers
        #-------------------------

        def sw_topRightEject_active_for_200ms(self, sw):
            if self.lock_lit and not self.multiball_running:
                self.ball_locked()
                return procgame.game.SwitchStop
            elif self.multiball_running:
                self.eject()
                return procgame.game.SwitchStop

                
        def sw_shooterLane_open_for_250ms(self,sw):
            if self.multiball_ready and not self.multiball_running:
                self.multiball_start()


        def sw_middleStandup_active(self,sw):
            if self.multiball_running:
                self.progress(0)

                return procgame.game.SwitchStop

        def sw_leftStandupRightRamp_active(self, sw):
            if self.multiball_running:
                self.progress(1)

                return procgame.game.SwitchStop

        def sw_rightStandupRightRamp_active(self, sw):
            if self.multiball_running:
                self.progress(2)

                return procgame.game.SwitchStop

#        def sw_flipperLwL_active(self, sw):
#            if self.multiball_started:
#                self.lane_change('left')
#
#
#        def sw_flipperLwR_active(self, sw):
#            if self.multiball_started:
#                self.lane_change('right')

