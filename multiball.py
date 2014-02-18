# Multiball Code
#
# This mode handles the ball lock count and the multiball features such as jackpots,how many balls are in play etc.
# All Idol functions are handles by the idol mode. The number of balls locked is not the same as the number of balls in the idol!

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import random
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Multiball(game.Mode):

	def __init__(self, game, priority):
            super(Multiball, self).__init__(game, priority)
            self.log = logging.getLogger('whirlwind.multiball')

            self.game.sound.register_sound('jackpot_attempt', sound_path+"jackpot_attempt.ogg")
            self.game.sound.register_sound('multiball_start_speech', speech_path+"ftp_wind.ogg")
            self.game.sound.register_sound('multiball_eject_speech', speech_path+"here_it_comes.ogg")
            self.game.sound.register_sound('jackpot_speech', speech_path+"feel_the_power.ogg")
            self.game.sound.register_sound('super_jackpot_speech', speech_path+"feel_the_power.ogg")

            self.game.sound.register_music('multiball_play', music_path+"multiball_play.ogg")

            self.flashers = ['rampBottomFlasher','rampLMFlasher','rampUMFlasher','rampTopFlasher','spinnerFlasher','bottomRightFlasher']
            self.lightning_flashers = ['lightningLeftFlasher','lightningMiddleFlasher','lightningRightFlasher']

            self.balls_needed = 3
            self.balls_in_play = 1


            self.lock_ball_score = 50000
            self.jackpot_base = 2000000
            self.jackpot_boost = 1000000
            self.jackpot_value = self.jackpot_base
            
            self.jackpot_lamps = ['millionPlus']
            self.jackpot_status = 'notlit'
            self.jackpot_worth_text =''
            self.super_jackpot_enabled = False
            self.super_jackpot_value = 2000000
            self.next_ball_ready = False
            self.ramp_lift_timer = 10

            #self.lock_lit = False
            self.mode_running = False
            self.balls_locked = 0
            self.multiball_started = False
            self.multiball_running = False
            self.end_callback = None

            
            self.reset()


        def reset(self):
            self.update_lamps()

            #add a setting to disable/enable resetting these
            self.jackpot_x = 1
            self.jackpot_collected = 0


        def multiball_lamps(self, enable=True):
            # Start the lamps doing a crazy rotating sequence:
            schedules = [0xffff000f, 0xfff000ff, 0xff000fff, 0xf000ffff, 0x000fffff, 0x00fffff0, 0x0fffff00, 0xfffff000]
            for index, lamp in enumerate(sorted(self.game.lamps.items_tagged('compass'), key=lambda lamp: lamp.number)):
                if enable:
                    sched = schedules[index%len(schedules)]
                    lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
                else:
                    lamp.disable()


        def update_lamps(self):
            if self.multiball_running:
                self.multiball_lamps()
            else:
                self.multiball_lamps(False)


        def mode_started(self):
            self.log.debug('multiball mode started')

            #set player stats for mode
            #self.lock_lit = self.game.get_player_stats('lock_lit')
            self.mode_running = self.game.get_player_stats('mode_running')
            self.balls_locked = self.game.get_player_stats('balls_locked')
            self.multiball_running = self.game.get_player_stats('multiball_running')
            self.jackpot_collected = self.game.get_player_stats('jackpot_collected')
            #self.multiball_started = self.game.get_player_stats('multiball_started')

        def mode_stopped(self):
            self.jackpot('cancelled')
            self.game.set_player_stats('balls_locked',self.balls_locked)
            self.game.set_player_stats('jackpot_collected',self.jackpot_collected)
            #self.game.set_player_stats('lock_lit',self.lock_lit)

        
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
                    self.game.set_player_stats('multiball_running',self.multiball_running)


                if self.multiball_running:
                    self.multiball_tracking()

        

        def update_score(self):
            score = self.game.current_player().score
            self.score_layer.set_text(locale.format("%d", score, True))

        def update_jackpot_worth(self):
            self.jackpot_worth_text= locale.format("%d", self.jackpot_value, True)+" X"+str(self.jackpot_x)

        def display(self, top, bottom, seconds, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_transition_reveal(text=top.upper(),row=0,seconds=seconds)
            self.game.score_display.set_transition_reveal(text=bottom.upper(),row=1,seconds=seconds)


        def strobe_flashers(self,time=0.2):
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
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='fast',time=time+0.6))

                flash(i,time,timer)
                timer+=time


        def multiball_start(self):
            self.log.debug('multiball start reached')

            #update the flag
            self.multiball_started = True
            self.game.set_player_stats('multiball_started',self.multiball_started)


            #update display
            self.display(top='feel the power',bottom='of the wind',seconds=3)

            #play speech
            start_speech_length = self.game.sound.play_voice('multiball_start_speech')
            
            #change music
            self.game.sound.stop_music()
            self.game.sound.play_music('multiball_play',-1)

            
            self.delay(name='multiball_eject_delay',delay=start_speech_length+0.5, handler=self.multiball_eject)


        def multiball_eject(self):
            self.log.debug('multiball eject reached')

            #make sure ramp is up
            self.game.switched_coils.drive('rampLifter')
            
            #kick out balls
            self.game.switched_coils.drive('leftLockKickback')
            #play speech
            self.game.sound.play_voice('multiball_eject_speech')

            #update trough tracking
            self.game.trough.num_balls_locked = 0
            self.balls_locked = 0
            
            #queue multiball effects
            self.delay(name='multiball_effects_delay',delay=0.5, handler=self.multiball_effects)
            

        def multiball_effects(self):
            #jackpot lit at start
            self.jackpot('lit')

            #spin wheels
            self.spin_wheels()

            #run flasher effects
            self.strobe_flashers()

            #start lamp effects
            self.multiball_lamps()

            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=3,allow_multiple_saves=True,time=10)
            

        def multiball_tracking(self):
            #end check
            if self.balls_in_play==1:
                #end tracking & update player stats
                self.multiball_running=False
                self.multiball_started = False
                self.game.set_player_stats('multiball_running',self.multiball_running) 
                self.game.set_player_stats('multiball_started',self.multiball_started)

                self.compass_level = self.game.get_player_stats('compass_level')
                self.game.set_player_stats('compass_level', self.compass_level+1)
                #add reset mode call to compass here to set next chase sequence

                #stop spinning wheels
                self.cancel_delayed('spin_wheels_repeat')

                #change music
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play', loops=-1)

                #light jackpot if not collected during multiball otherwise cancel
                if self.jackpot_collected==0:
                    self.jackpot('lit')
                    self.delay(name='jackpot_timeout', event_type=None, delay=15, handler=self.jackpot, param='cancelled')
                else:
                    self.jackpot('cancelled')

                #callback from compass
                if self.end_callback:
                    self.log.debug('Multiball End Callback Called')
                    self.end_callback()


        def jackpot_helper_display(self):
            time=3
            self.display(top='shoot skyway',bottom='to lite jackpot',seconds=time)


        def jackpot_collected_display(self):
            time=3
            self.display(top='j a c k p o t',bottom=locale.format("%d", self.jackpot_value*self.jackpot_collected*self.jackpot_x, True),seconds=time)
            self.delay(name='reset_jackpot',delay=time,handler=lambda:self.jackpot('unlit'))


        def jackpot_raised_display(self,num):
            time=2
            self.jackpot_value+=num
            self.display(top='jackpot now',bottom=locale.format("%d", self.jackpot_value, True),seconds=time)


        def jackpot(self,status=None):

                self.jackpot_status = status
         
                if status=='lit':
                    #lift ramp for timed period to allow easier jackpot shot
                    self.game.switched_coils.drive('rightRampLifter')
                    self.delay(name='ramp_down_timer',delay=self.ramp_lift_timer,handler=self.game.coils['rampDown'].pulse)
                    
                    #set lamp
                    self.game.effects.drive_lamp('millionPlus','fast')
                    #set flasher for timed period
                    self.game.switched_coils.drive(name='compassFlasher',style='fast',time=1)
                    #update display
                    self.display(top='jackpot lit',bottom='',seconds=2)
                    #update score
                    self.game.score(50000)
                    #play speech
                    #self.game.sound.play('hit_jackpot')

                elif status=='unlit':
                    #put ramp down so jackpot can be relit
                    self.game.coils['rampDown'].pulse()
                    #tell player what to do
                    self.jackpot_helper_display()
                   

                elif status=='made':
                    self.game.effects.drive_lamp('millionPlus','off')
                    #self.game.switched_coils.disable('compassFlasher')

                    self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)
                    self.strobe_flashers(0.4)
                    self.game.sound.play_voice('jackpot_speech')
                    self.game.score(self.jackpot_value*self.jackpot_x)
                    self.jackpot_collected+=1
                    #self.game.effects.drive_lamp(self.jackpot_lamps[self.jackpot_collected-1],'smarton')

                    if self.jackpot_collected>10:
                        self.super_jackpot_collected()
                    else:
                        #update display
                        self.jackpot_collected_display()
                        #speech
                        self.game.sound.play('jackpot_speech')

                    
                elif status=='cancelled':
                    self.game.effects.drive_lamp('millionPlus','off')
                    #self.game.switched_coils.disable('compassFlasher')


     
        def super_jackpot_display(self):
            pass


        def super_jackpot_collected(self):
            pass
            #reset jackpot count to start again
            self.jackpot_collected=0


        def spin_wheels(self):
            num=random.randint(50,200)
            self.game.coils.spinWheelsMotor.pulse(num)
            self.delay(name='spin_wheels_repeat',delay=0.7,handler=self.spin_wheels)


        #switch handlers
        #---------------------------

        def sw_rightRampMadeTop_active(self, sw):
            if self.multiball_running:
                if self.jackpot_status!='lit':
                    self.jackpot('lit')

                #raise jackpot
                self.jackpot_raised_display(100000)

                return procgame.game.SwitchStop


        def sw_leftRampMadeTop_active(self, sw):
            if self.multiball_running and self.jackpot_status=='lit':
                self.jackpot('made')

                return procgame.game.SwitchStop


        #lock handlers to update trough counters once multiball started
        def sw_lock1_inactive_for_500ms(self, sw):
            if self.multiball_started:
                self.game.trough.num_balls_in_play+=1


        def sw_lock2_inactive_for_500ms(self, sw):
            if self.multiball_started:
                self.game.trough.num_balls_in_play+=1


        def sw_lock3_inactive_for_500ms(self, sw):
            if self.multiball_started:
                self.game.trough.num_balls_in_play+=1
                

       