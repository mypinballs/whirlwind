# -------------------------
# Spinner Mode - possible mode name change to OUter Loops
#
# Controls Spinner Value
# Cellar award change controlled in cellar mode
# Effects for Outer Loops 
#
# Copyright (C) 2013 myPinballs, Orange Cloud Software Ltd
#
# -------------------------

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

class Spinner(game.Mode):

	def __init__(self, game, priority):
            super(Spinner, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.spinner')

            self.game.sound.register_sound('spinner', sound_path+"spinner.aiff")

            self.flashers = ['bottomRightFlasher','rampTopFlasher','rampUMFlasher','rampLMFlasher','rampBottomFlasher']
            #var setup
            self.value = [1,2,5,10]
            self.inc_value = 10
            self.timer = 10
            self.spinner_double_timer = 2.5


        def reset(self):
            #general
            self.level = 0
            self.spins = 0

           
        def mode_started(self):
            self.level = self.game.get_player_stats('spinner_level')

            #call reset
            self.reset()


        def mode_stopped(self):
            self.game.set_player_stats('spinner_level',self.level)
     
      
        def spin_text(self):
            #set text layer 
            self.game.score_display.set_text(self.spin_value+'K Per Spin'.upper(),0,'center',seconds=2)
            self.cancel_delayed('remove_text')
            self.delay(name='remove_text', event_type=None, delay=2, handler=lambda: self.game.display.rdc.remove_layer(id=text_layer_id))

  
        def play_animation(self):
            self.spin_text()
            

        def calc_value(self):
            if self.level<=3:
                self.spin_value=self.value[self.level]
            else:
                self.spin_value=self.level-1*self.inc_value

            if self.game.switches.leftInlane.time_since_change()<=self.spinner_double_timer+1:
                self.spin_value = self.spin_value*2

        def score(self):
            self.game.score(self.spin_value*1000)


#        def random_flash(self):
#             i= random.randint(0, len(self.flashers)-1)
#             self.game.effects.drive_flasher(self.flashers[i],'fast',0.2)

#        def strobe_flashers(self,dirn):
#            if dirn==1:#right
#                self.flashers.reverse()
#
#            self.game.effects.strobe_flasher_set(self.flashers,time=0.07,overlap=0.02,repeats=3)

        def strobe_flashers(self,flashers,time=0.1):
            timer = 0
            repeats = 1

            sequence=[]
            for j in range(repeats):
                sequence += flashers

            for i in range(len(sequence)):

                def flash(i,time,delay):
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='super',time=time+0.1))

                flash(i,time,timer)
                timer+=time

            
        def progress(self):
            self.spins+=1
            self.calc_value()
            self.score()
            self.game.sound.play_voice('spinner')


        def sw_spinner_active(self, sw):
            self.progress()

        def sw_rightLoopTop_active(self,sw):
            if self.game.switches.rightLoopBottom.time_since_change()<=0.5:
                self.strobe_flashers(self.flashers)

        def sw_leftLoopTop_active(self,sw):
            if self.game.switches.leftLoopBottom.time_since_change()<=0.5:
                flashers = self.flashers
                flashers.reverse()
                self.strobe_flashers(flashers)

        def sw_leftInlane_active(self,sw):
            self.game.switched_coils.drive(name='spinnerFlasher',style='fast',time=self.spinner_double_timer)
            self.game.effects.drive_lamp('rightSpinner','timeout',self.spinner_double_timer)

