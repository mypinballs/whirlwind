# Multiball Code
#
# This mode handles the ball lock count and the multiball features such as jackpots,how many balls are in play etc.
# All Idol functions are handles by the idol mode. The number of balls locked is not the same as the number of balls in the idol!

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Multiball(game.Mode):

	def __init__(self, game, priority):
            super(Multiball, self).__init__(game, priority)

            self.game.sound.register_sound('jackpot_attempt', sound_path+"jackpot_attempt.ogg")

            self.game.sound.register_sound('multiball_start_speech', speech_path+"here_it_comes.ogg")
            self.game.sound.register_sound('jackpot_speech', speech_path+"feel_the_power.ogg")
            self.game.sound.register_sound('super_jackpot_speech', speech_path+"feel_the_power.ogg")

            self.game.sound.register_music('multiball_play', music_path+"multiball_play.ogg")

            self.flashers = ['bottomRightFlasher','spinnerFlasher','rampTopFlasher','rampUMFlasher','rampLMFlasher','rampBottomFlasher','dropTargetFlasher','compassFlasher']

            self.balls_needed = 3
            self.balls_in_play = 1


            self.lock_ball_score = 50000
            self.jackpot_base = 1000000
            self.jackpot_boost = 1000000
            self.jackpot_value = self.jackpot_base
            self.jackpot_x = 1
            self.jackpot_collected = 0
            self.jackpot_lamps = ['millionPlus']
            self.jackpot_status = 'notlit'
            self.jackpot_worth_text =''
            self.super_jackpot_enabled = False
            self.super_jackpot_value = 2000000
            self.next_ball_ready = False

            self.lock_lit = False
            self.mode_running = False
            self.balls_locked = 0
            self.multiball_started = False
            self.multiball_running = False

            
            self.reset()


        def reset(self):
            self.update_lamps()


        def mode_started(self):
            #set player stats for mode
            self.lock_lit = self.game.get_player_stats('lock_lit')
            self.mode_running = self.game.get_player_stats('mode_running')
            self.balls_locked = self.game.get_player_stats('balls_locked')
            self.multiball_running = self.game.get_player_stats('multiball_running')
            self.multiball_started = self.game.get_player_stats('multiball_started')

        def mode_stopped(self):
            self.jackpot('cancelled')

        
        def mode_tick(self):
            if self.multiball_started:
                self.balls_in_play = self.game.trough.num_balls_in_play

                #debug
                #self.balls_in_play=3
                #-------------------------------------------
                #debug_ball_data = str(self.balls_in_play)+":"+str(self.game.trough.num_balls())+":"+str(self.game.trough.num_balls_locked)+":"+str(self.game.trough.num_balls_to_launch)+":"+str(self.multiball_running)
                #self.game.set_status(debug_ball_data)
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
            self.game.score_display.set_text(top.upper(),0,'center',seconds=seconds)
            self.game.score_display.set_text(bottom.upper(),1,'center',seconds=seconds)


        def multiball_start(self):
            #update display
            self.display(top='feel the power',bottom='of the wind',seconds=3)
            #kick out balls
            self.game.switched_coils.drive('leftLockKickback')
            
            #change music
            self.game.sound.stop_music()
            self.game.sound.play_music('multiball_play',-1)

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

                #change music
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play', loops=-1)

                #light jackpot if not collected during multiball otherwise cancel
                if self.jackpot_collected==0:
                    self.jackpot('lit')
                    self.delay(name='jackpot_timeout', event_type=None, delay=10, handler=self.jackpot, param='cancelled')
                else:
                    self.jackpot('cancelled')
        

        def jackpot_collected_display(self,num):
            time=3
            self.display(top='j a c k p o t',bottom=locale.format("%d", self.jackpot_value*self.jackpot_collected*self.jackpot_x, True),seconds=time)
            self.delay(name='reset_jackpot',delay=time,handler=lambda:self.jackpot('unlit'))


        def jackpot(self,status=None):

                self.jackpot_status = status
         
                if status=='lit':
                    #set flasher
                    self.game.switched_coils.drive('compassFlasher','medium')
                    #update display
                    self.display(top='jackpot lit',bottom='',seconds=2)
                    #update score
                    self.game.score(50000)
                    #play speech
                    #self.game.sound.play('hit_jackpot')

                elif status=='unlit':
                    self.game.coils.flasherLiteJackpot.schedule(schedule=0x30003000 , cycle_seconds=0, now=True)
                    self.game.coils.divertorHold.disable()
                    self.game.coils.topLockupHold.disable()

                    #update display
                    if self.jackpot_collected<4:
                        self.multiball_display(self.jackpot_collected)
                    else:
                        self.super_jackpot_display()

                elif status=='made':
                    self.game.switched_coils.drive('compassFlasher','off')
                    self.game.lampctrl.play_show('jackpot', repeat=False,callback=self.game.update_lamps)#self.restore_lamps
                    self.strobe_flashers(0.4)
                    self.game.score(self.jackpot_value*self.jackpot_x)
                    self.jackpot_collected+=1
                    self.game.effects.drive_lamp(self.jackpot_lamps[self.jackpot_collected-1],'smarton')

                    if self.jackpot_collected>10:
                        self.super_jackpot_collected()
                    else:
                        #update display
                        self.jackpot_collected_display()
                        #speech
                        self.game.sound.play('jackpot_speech')

                    
                elif status=='cancelled':
                    self.game.switched_coils.drive('compassFlasher','off')


        def strobe_flashers(self,time):
            timer = 0
            for j in range(3):
                for i in range(len(self.flashers)):

                    def flash(i,time,delay):
                        self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=self.flashers[i],style='fast',time=time+0.6))

                    flash(i,time,timer)
                    timer+=time


        def super_jackpot_display(self):
            pass


        def super_jackpot_collected(self):
            pass
            #reset jackpot count to start again
            self.jackpot_collected=0


        def sw_topRightEject_active(self, sw):
            if self.multiball_running:
                if self.jackpot_status!='lit':
                    self.jackpot('lit')
                
                value = 100000
                self.jackpot_value+=value
                self.display(top='jackpot raised',bottom=locale.format("%d", value, True),seconds=2)


        def sw_leftRampMadeTop_active(self, sw):
            if self.multiball_running:
                self.jackpot('made')
                

       