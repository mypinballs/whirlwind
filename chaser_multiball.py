#Upper Left Ramp Mode

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

class ChaserMultiball(game.Mode):

	def __init__(self, game, priority):
            super(ChaserMultiball, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.chaser_multiball')

            self.game.sound.register_sound('shot_lit', sound_path+"compass_target_lit.ogg")
            self.game.sound.register_sound('shot_unlit', sound_path+"thunder_crack.ogg")
            self.game.sound.register_music('lock_lit', music_path+"lock_lit.ogg")
            self.game.sound.register_music('end', music_path+"lock_lit_end.ogg")
            self.game.sound.register_music('multiball_play', music_path+"multiball_play.ogg")

            self.game.sound.register_sound('take_cover_now', speech_path+"take_cover_now.ogg")
            self.game.sound.register_sound('multiball_eject_speech', speech_path+"here_it_comes.ogg")
            self.game.sound.register_sound('million_speech', speech_path+"ooh_million.ogg")
            self.game.sound.register_sound('whirlwind_speech', speech_path+"whirlwind.ogg")

            self.flashers = ['rampBottomFlasher','rampLMFlasher','rampUMFlasher','rampTopFlasher','spinnerFlasher','bottomRightFlasher']
            self.lightning_flashers = ['lightningLeftFlasher','lightningMiddleFlasher','lightningRightFlasher']
            
            self.lamps = ['swBottom','swTop','2tolls','seTop']
            self.jackpot_lit_lamp_data = ['millionPlus','million','release']


            self.enter_value = 10
            self.made_value_base = 50000
            self.made_value_boost = 10000
            self.made_value_max = 100000
            self.skyway_toll_boost = 3
            self.super_combo_multiplier = 10
            self.combo_multiplier = 2
            self.million_value = 1000000
            self.million_timer = 30 #change to setting
            self.jackpots_collected = 0
            
            self.lane_unlit_value = 5000
            self.lane_lit_value = 1000

            self.balls_needed = 2
            self.next_ball_ready = False
            self.virtual_lock = False
            self.multiball_info_text_flag = 0
            self.end_callback= None

            
        def reset(self):
            self.reset_combos()
            self.shots_made = 0
            self.lane_flag = [False,False,False,False]
            self.lite_million(False)
            self.lock_lit=False
            self.reset_lamps()
            

        def reset_combos(self):
            self.combo = False
            self.super_combo = False

        
        def update_lamps(self):
            self.log.info("Updating Storm Chaser Shot Lamps")
            for i in range(len(self.lamps)):
                if self.lane_flag[i]:
                    self.game.effects.drive_lamp(self.lamps[i],'on')
                else:
                    self.game.effects.drive_lamp(self.lamps[i],'fast')


        def set_lamps_help(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'fast')


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
        
        def jackpot_lit_lamps(self,enable=True):
            schedule = [0x0000000f, 0x000000f0, 0x000ccc00]
            for i in range(len(self.jackpot_lit_lamp_data)):
                lamp = self.jackpot_lit_lamp_data[i]
		if enable:
                    #sched = schedules[index%len(schedules)]
                    self.game.lamps[lamp].schedule(schedule=schedule[i], cycle_seconds=0, now=False)
		else:
                    self.game.lamps[lamp].disable()
            
            

            
        def mode_started(self):            
            self.multiball_ready = self.game.get_player_stats('quick_multiball_ready')
            self.multiball_started = self.game.get_player_stats('quick_multiball_started')
            self.multiball_running = self.game.get_player_stats('quick_multiball_running')
            self.million_lit = self.game.get_player_stats('million_lit')

            self.reset()
            
            
        def mode_stopped(self):
            self.lock_lit=False
            self.multiball_ready = False
            self.game.set_player_stats('qm_lock_lit',self.lock_lit)
            self.game.set_player_stats('quick_multiball_ready',self.multiball_ready)
            self.game.set_player_stats('quick_jackpots_collected',self.jackpots_collected)
            

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
            self.game.set_player_stats('qm_lock_lit',self.lock_lit)

            self.display(top='Storm Chaser',bottom='Multiball Is Lit',seconds=5)

            self.game.sound.stop_music()
            self.game.sound.play_music('lock_lit',-1)
            self.delay(name='lock_lit_announce',delay=1,handler=lambda:self.game.sound.play_voice('take_cover_now'))

            self.game.effects.drive_lamp('lock','fast')
            self.game.effects.drive_lamp('topDropQuickMB','fast')

            self.spin_wheels()

            #lift ramp with delay
            self.delay(name='lift_ramp_delay',delay=0.5,handler=lambda:self.game.switched_coils.drive('rampLifter'))
           

        def ball_locked(self):

            self.display(top='Storm Chaser',bottom='Multiball Ready',seconds=6)

            #set multiball ready flag
            self.multiball_ready = True
            self.game.set_player_stats('quick_multiball_ready',self.multiball_ready)
            self.log.info('Storm Chaser Multiball Ready')

            #update lock lit flag
            self.lock_lit=False
            self.game.set_player_stats('qm_lock_lit',self.lock_lit)

            self.game.sound.play_voice('whirlwind_speech')
            
            #flasher effect
            self.lock_flashers()

            #cancel lock lamp
            self.game.effects.drive_lamp('lock','off')
            
            #queue the next ball launch
            self.delay(name='launch_next_ball',delay=0.5,handler=self.launch_next_ball)
            audits.record_value(self.game,'ballLocked')
            
            #queue multiball effects
            self.delay(name='multiball_effects_delay',delay=1, handler=self.multiball_effects)


        def launch_next_ball(self):
            if not self.virtual_lock: #skyway should handle the eject saucer with corect delay if virtual lock
                self.game.trough.launch_balls(1,callback=self.launch_callback,stealth=False) #stealth false, bip +1
            self.next_ball_ready = True
            self.virtual_lock = False
            self.game.ball_save.start(time=10)
            
            
        def launch_callback(self):
            pass
        
            
        def spin_wheels(self):
            num=random.randint(50,150)
            self.game.coils.spinWheelsMotor.pulse(num)
            self.delay(name='spin_wheels_repeat',delay=0.8,handler=self.spin_wheels)


        def display(self, top, bottom, seconds, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_transition_reveal(text=top.upper(),row=0,seconds=seconds)
            self.game.score_display.set_transition_reveal(text=bottom.upper(),row=1,seconds=seconds)

        
        def display_lock_ready_text(self,time=3):
           self.display(top='Storm Chaser',bottom='Multiball Is Lit',seconds=time)


        def display_million_text(self,time=2):
            self.display(top='1 Million',bottom='Million',seconds=time)


        def display_multiball_info(self,time=3):
            if self.multiball_info_text_flag%2==0:
                self.display(top='Shoot Lit Shots',bottom='To Chase Storm',seconds=time)
            else:
                self.display(top='All Shots Lit',bottom='Lites Jackpot',seconds=time)

            if self.multiball_info_text_flag<10:
                self.multiball_info_text_flag+=1
                self.cancel_delayed('display_multiball_info_repeat')
                self.delay(name='display_multiball_info_repeat',delay=time+0.5,handler=self.display_multiball_info,param=time)
            else:
                self.multiball_info_text_flag = 0
                self.cancel_delayed('display_multiball_info_repeat')


        def strobe_flashers(self,time=0.1):
            timer = 0
            repeats = 6

            #lightning flashers
            self.game.effects.strobe_flasher_set(self.lightning_flashers,time=time,overlap=0.2,repeats=repeats)

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
                
                
        def multiball_effects(self):

            #spin wheels
            self.spin_wheels()

            #run flasher effects
            self.strobe_flashers()

            #disable all regular lamps
            for lamp in self.game.lamps:
		lamp.disable()
            
            #start lamp effects
            self.set_lamps_help()
            self.compass_lamps()


        def multiball_start(self):
            self.log.debug('multiball start reached')

            #update the flag
            self.multiball_started = True
            self.game.set_player_stats('quick_multiball_started',self.multiball_started)

            #display help info
            self.display_multiball_info(3)
            
            #make sure ramp is down
            self.skyway_entrance('down')
            
            #play speech
            start_speech_length = self.game.sound.play_voice('multiball_eject_speech')

            #change music
            self.game.sound.stop_music()
            self.game.sound.play_music('multiball_play',-1)

            self.delay(name='multiball_eject_delay',delay=start_speech_length+0.5, handler=self.multiball_eject)

            audits.record_value(self.game,'quickMultiballStarted')


        def multiball_eject(self):
            self.log.debug('multiball eject reached')
            
            #kick out ball
            self.game.switched_coils.drive('topEject')

            #update trough tracking
            #self.game.trough.num_balls_locked = 0
            #self.balls_locked = 0
            self.game.trough.num_balls_in_play+=1
            
            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=2,allow_multiple_saves=True,time=10)


        def multiball_tracking(self):
            #end check
            if self.balls_in_play==1:
                #end tracking & update player stats
                self.multiball_running=False
                self.multiball_started = False
                self.multiball_ready = False
                
                self.game.set_player_stats('quick_multiball_running',self.multiball_running)
                self.game.set_player_stats('quick_multiball_started',self.multiball_started)
                self.game.set_player_stats('quick_multiball_ready',self.multiball_ready)
               
                
                #stop spinning wheels
                self.cancel_delayed('spin_wheels_repeat')

                #cancel award
                self.lite_million(False)
                #stop compass
                self.compass_lamps(False)
                
                #disable all lamps
                for lamp in self.game.lamps:
                    lamp.disable()

                #restore lamp states from other modes
                self.game.update_lamps()

                #change music
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play', loops=-1)

                #mulitball ended callback
                if self.end_callback:
                    self.log.debug('Quick Multiball End Callback Called')
                    self.end_callback()


        def spin_wheels(self):
            range=[]
            delay=0
            if self.multiball_started:
                range=[50,200]
                delay=0.7
            else:
                range=[50,150]
                delay=0.8

            num=random.randint(range[0],range[1])
            self.game.coils.spinWheelsMotor.pulse(num)
            self.delay(name='spin_wheels_repeat',delay=0.7,handler=self.spin_wheels)


        def skyway_entrance(self,dirn):
            if dirn=='up' and self.game.switches.rightRampDown.is_active():
                self.game.switched_coils.drive('rampLifter')
            elif dirn=='down' and self.game.switches.rightRampDown.is_inactive():
                self.game.coils['rampDown'].pulse()


        def eject(self):
            self.game.switched_coils.drive('topEject')


        def lite_million(self,enable=True):
            if enable:
                self.million_lit=True
                self.log.debug('Million is Lit')
                
                self.skyway_entrance('up') #raise ramp

                self.game.switched_coils.drive(name='rampUMFlasher',style='fast') #schedule million flasher for unlimited time
                self.jackpot_lit_lamps()

                if self.jackpots_collected>=3: #setup a timeout for jackpots after first few
                    self.delay(name='million_timer',delay=self.million_timer,handler=self.timeout_million)
            else:
                self.million_lit=False
                self.skyway_entrance('down') #lower ramp
                self.game.switched_coils.drive(name='rampUMFlasher',style='off')
                self.jackpot_lit_lamps(False)

            self.million_speech(enable)
            self.game.set_player_stats('million_lit',self.million_lit)
           

        def timeout_million(self):
            self.lite_million(False)
            self.reset()


        def award_million(self):
            self.cancel_delayed('million_timer')
            self.cancel_delayed('million_speech')
            
            self.display_million_text()
            self.game.score(self.million_value)
            #self.game.sound.play_voice('whirlwind_speech')
            self.delay(name='award_speech_delay',delay=1,handler=lambda:self.game.sound.play_voice('whirlwind_speech'))
            self.game.switched_coils.drive(name='rampUMFlasher',style='fast',time=1)

            #queue the reset to setup next jackpot
            self.delay(name='multiball_award_reset',delay=2, handler=self.award_reset)

            self.jackpots_collected+=1
            #update audits
            audits.record_value(self.game,'chaserJackpotCollected')


        def award_reset(self):
            self.reset()
            self.set_lamps_help()


        def progress(self,id):
            self.update_lamps()

            if self.lane_flag[id] == False:

                self.shots_made +=1
                self.lane_flag[id]=True;
                #update player stats var
                #self.game.set_player_stats('chaser_shot_flag',self.lane_flag)
                self.log.debug("chaser shot made: %s",self.lamps[id])
                self.game.score(self.lane_unlit_value)

                #play sounds
                if self.shots_made ==4:
                    self.lite_million()
                else:
                    self.game.sound.play('shot_unlit')
                    self.game.effects.drive_lamp(self.lamps[id],'smarton')

            else:
                self.game.score(self.lane_lit_value)
                #play sounds
                self.game.sound.play('shot_lit')

            self.log.debug(self.lane_flag)
            self.log.debug(self.shots_made)



        #switch handlers
        #------------------------
        def sw_leftRampMadeTop_active(self, sw):
            if self.multiball_running and self.million_lit:
                self.award_million()
                

        def sw_topRightEject_active_for_200ms(self, sw):
            if self.lock_lit and not self.multiball_running:
                self.ball_locked()
                return procgame.game.SwitchStop
            elif self.multiball_running:
                self.eject()
                return procgame.game.SwitchStop

                
        def sw_shooterLane_open_for_1s(self,sw):
            if self.multiball_ready and not self.multiball_running:
                self.multiball_start()
        
        
        def sw_leftLoopTop_active(self,sw):
            if self.game.switches.leftLoopBottom.time_since_change()<=0.5 and self.multiball_running:
                self.progress(0)

                return procgame.game.SwitchStop
        
        def sw_innerLoop_active(self, sw):
            if self.multiball_running:
                self.progress(1)

                return procgame.game.SwitchStop
            
        def sw_rightRampMadeTop_active(self, sw):
            if self.multiball_running:
                self.progress(2)

                return procgame.game.SwitchStop
            
        def sw_rightLoopTop_active(self,sw):
            if self.game.switches.rightLoopBottom.time_since_change()<=0.5 and self.multiball_running:
                self.progress(3)

                return procgame.game.SwitchStop
            