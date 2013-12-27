#Upper Left Ramp Mode

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

class Ramp(game.Mode):

	def __init__(self, game, priority, mode1, mode2):
            super(Ramp, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.ramp')
            self.skyway = mode1
            self.cellar = mode2

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('enter_left_ramp', sound_path+"enter_left_ramp.ogg")
            self.game.sound.register_sound('made_left_ramp', sound_path+"made_left_ramp.ogg")

            self.enter_value = 10
            self.made_value_base = 50000
            self.made_value_boost = 10000
            self.made_value_max = 100000
            self.skyway_toll_boost = 3

            self.reset()


        def reset(self):
            pass

        
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
            
        def mode_stopped(self):
            pass

        def display_text(self, count, value, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_text(str(count)+' skyway tolls'.upper(),0,'center',seconds=2)
            self.game.score_display.set_text('+'+locale.format("%d", value, True),1,'center',seconds=2)


        def update_count(self):
            
            self.shots_made+=1

            #update audit tracking
            self.game.game_data['Audits']['Left Ramps'] += 1
    
        def score(self,value):
            self.game.score(value)

        def update_tolls(self):
            tolls = self.skyway.inc_tolls(self.skyway_toll_boost)

            value = 0
            if value<self.made_value_max:
                value = self.made_value_base+(self.made_value_boost*self.shots_made)
            else:
                value = self.made_value_max

            self.display_text(tolls,value)
            self.score(value)

        def lite_cellar(self):
            self.cellar.lite_cellar(20)

        def made(self):
            self.update_count()
            self.update_tolls()
            self.lite_cellar()
            self.game.sound.play('made_left_ramp')

        def spin_wheels(self):
            self.game.coils.spinWheelsMotor.pulse()

        def sw_leftRampEnter_active(self, sw):
            self.game.score(10)
            self.game.sound.play('enter_left_ramp')

        def sw_leftRampMadeTop_active(self, sw):
            self.made()

        def sw_leftRampMadeBottom_active(self, sw):
            self.spin_wheels()