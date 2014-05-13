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

class Ramp(game.Mode):

	def __init__(self, game, priority, mode1, mode2):
            super(Ramp, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.ramp')
            self.skyway = mode1
            self.cellar = mode2

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('enter_left_ramp', sound_path+"enter_left_ramp.ogg")
            self.game.sound.register_sound('made_left_ramp', sound_path+"made_left_ramp.ogg")
            self.game.sound.register_sound('million_speech', speech_path+"ooh_million.ogg")
            self.game.sound.register_sound('whirlwind_speech', speech_path+"whirlwind.ogg")

            self.lightning_flashers = ['lightningLeftFlasher','lightningMiddleFlasher','lightningRightFlasher']

            self.enter_value = 10
            self.made_value_base = 50000
            self.made_value_boost = 10000
            self.made_value_max = 100000
            self.skyway_toll_boost = 3
            self.super_combo_multiplier = 10
            self.combo_multiplier = 2
            self.million_value = 1000000
            self.million_timer = 30 #change to setting
           
        
        def reset(self):
            self.reset_combos()

        def reset_combos(self):
            self.combo = False
            self.super_combo = False

        
#        def update_lamps(self):
#            for i in range(self.lamps):
#                self.game.effects.drive_lamp(self.lamps[i],'on')
#
#        def set_lamps(self):
#            for i in range(self.lamps):
#                self.game.effects.drive_lamp(self.lamps[i],'smarton')

            
        def mode_started(self):
            self.shots_made = 0
            self.multiball_ready = self.game.get_player_stats('multiball_ready')
            self.million_lit = self.game.get_player_stats('million_lit')

            self.reset()
            
        def mode_stopped(self):
            pass

        def display_text(self, count, value, opaque=True, repeat=False, hold=False, frame_time=3):
            top_text=str(count)+' skyway tolls'
            bottom_text = '+'+locale.format("%d", value, True)

            if self.super_combo:
                top_text = 'Super Combo'
                bottom_text = 'Millions'
            elif self.combo:
                top_text = 'Skyway Combo'
                bottom_text = str(count)+' tolls'

            self.game.score_display.set_text(top_text.upper(),0,'center',seconds=2)
            self.game.score_display.set_text(bottom_text.upper(),1,'center',seconds=2)


        def display_million_text(self):
            self.game.score_display.set_text('1 million'.upper(),0,'center',seconds=2)
            self.game.score_display.set_text('million'.upper(),1,'center',blink_rate=0.1,seconds=2)

        def million_speech(self,enable=True):
            if enable:
                self.game.sound.play_voice('million_speech')
                self.delay('million_speech_repeat',delay=10,handler=self.million_speech)
            else:
                self.cancel_delayed('million_speech_repeat')


        def update_count(self):
            self.shots_made+=1


        def score(self,value):
            self.game.score(value)
            

        def update_tolls(self):
            if self.combo or self.super_combo:
                tolls = self.skyway.inc_tolls(self.skyway_toll_boost*self.combo_multiplier)
            else:
                tolls = self.skyway.inc_tolls(self.skyway_toll_boost)

            value = 0
            if not self.super_combo:
                if value<self.made_value_max:
                    value = self.made_value_base+(self.made_value_boost*self.shots_made)
                else:
                    value = self.made_value_max
            else:
                value = self.made_value_max*self.super_combo_multiplier

            self.display_text(tolls,value)
            self.score(value)


        def lite_cellar(self):
            self.cellar.lite_cellar(20)


        def made(self):
            self.check_combo()
            self.update_count()
            self.update_tolls
            self.game.effects.strobe_flasher_set(flasher_list=self.lightning_flashers, time=0.2, repeats=3)

            self.game.sound.play('made_left_ramp')

            if not self.game.get_player_stats('multiball_started') and not self.game.get_player_stats('quick_multiball_started'):
                if self.shots_made%5==0: #new feature :) every 5 ramps light the cellar hurryup shot!
                    self.cellar.hurryup()
                else:
                    self.cellar.lite_cellar(20)


            #update audits
            audits.record_value(self.game,'thunderRampMade')


        def spin_wheels(self):
            self.game.coils.spinWheelsMotor.pulse(200)


        def check_combo(self):
            #combo is left loop then ramp - gives double skyway tolls
            #super combo is left loop, inner loop then ramp - gives 10 times max skyway value (1 million)
    
            if self.game.switches.leftLoopTop.time_since_change()<=4 and self.game.switches.rightLoopBottom.time_since_change()<=3:
                if self.game.switches.innerLoop.time_since_change()<=2:
                    self.super_combo = True
                else:
                    self.combo = True


        def lite_million(self,enable=True):
            if enable:
                self.million_lit=True
                self.log.debug('Million is Lit')

                self.game.switched_coils.drive(name='rampUMFlasher',style='fast',time=1)#schedule million flasher for timed period
                self.game.effects.drive_lamp('million','fast')

                self.delay(name='million_timer',delay=self.million_timer,handler=self.timeout_million)
            else:
                self.game.effects.drive_lamp('million','off')
                self.million_lit=False

            self.million_speech(enable)
            self.game.set_player_stats('million_lit',self.million_lit)
           

        def timeout_million(self):
            self.lite_million(False)


        def award_million(self):
            self.cancel_delayed('million_timer')
            self.cancel_delayed('million_speech')
            
            self.display_million_text()
            self.game.score(self.million_value)
            self.game.sound.play_voice('whirlwind_speech')
            self.game.switched_coils.drive(name='rampUMFlasher',style='fast',time=1)

            #reset
            self.lite_million(False)

            #update audits
            audits.record_value(self.game,'millionCollected')

        #switch handlers
        #-------------------------
        
        def sw_leftRampEnter_active(self, sw):
            self.game.score(10)
            self.game.sound.play('enter_left_ramp')

        def sw_leftRampMadeTop_active(self, sw):
            self.made()
            if self.million_lit:
                self.award_million()

        def sw_leftRampMadeBottom_active(self, sw):
            self.spin_wheels()
            self.reset_combos()

