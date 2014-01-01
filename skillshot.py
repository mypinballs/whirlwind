#-----------------------------------------
#
# SkillShot Mode
#
# Whirlwind v2 - by myPinballs
# Copyright 2013 Orange Cloud Software Ltd.
#
#-----------------------------------------

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


class Skillshot(game.Mode):

	def __init__(self, game, priority, mode1=None):
            super(Skillshot, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.skillshot')
            self.drops = mode1

            self.game.sound.register_sound('skill_shot_hit', sound_path+"skill_shot.ogg")

            self.lamps = ['shot','skill','super']
            self.flasher=['dropTargetFlasher']
            
            self.top_value = 300000
            self.mid_value = 200000
            self.bottom_value = 100000
            self.divider = 100000


        def reset(self):

            self.skillshot_in_progress = False
            self.game.set_player_stats('skillshot_in_progress',self.skillshot_in_progress)

            self.level = 1
            self.speed = 2
            self.value = 0
            self.display_repeats = 0
            self.display_repeating = False
            self.reset_lamps()


        def mode_started(self):
            #load player vars
            self.level =self.game.get_player_stats('skillshot_level')

            self.reset()

            #queue the lamp sequence
            self.delay(name='lamp_sequence_delay', event_type=None, delay=2, handler=self.lamp_sequence)

            
        
        def mode_stopped(self):
            self.game.set_player_stats('skillshot_level',self.level)
            self.game.set_player_stats('skillshot_in_progress',self.skillshot_in_progress)
           
            self.cancel_delayed('lamp_delay')
            self.cancel_delayed('lamp_repeat')
            self.reset_lamps()

            #stop shooter grove and play main play music
            self.game.sound.stop_music()
            #start main play tune
            self.game.sound.play_music('general_play', loops=-1)



        def clear(self):
            self.skillshot_in_progress = False
            self.game.modes.remove(self)

        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')

        def update_lamps(self):
            pass


        def lamp_sequence(self):
            #create a strip of moving lights
            timer=0
            interval=0.2 #1.0/(self.speed*self.level)

            for lamp in self.lamps:
                self.delay(name='lamp_delay',delay=timer,handler=self.set_lamp, param=lamp)
                timer+=interval

            self.delay(name='lamp_repeat',delay=timer,handler=self.lamp_sequence)

        def set_lamp(self,lamp):
            interval=0.2
            self.game.effects.drive_lamp(lamp,'timedon',interval)



        def award_score(self):
            self.game.score(self.value)


        def play_sound(self):
            self.game.sound.play('skill_shot_hit')
            

        def display_text(self,seconds=3, blink_rate=0.1, opaque=True, repeat=False, hold=False):

            value =self.value-self.display_repeats*self.divider

            if not self.display_repeating: #do not show text again if display repeating scoring
                self.game.score_display.set_text('super skill shot'.upper(),0,'center',seconds=seconds, blink_rate=blink_rate)
            self.game.score_display.set_text(locale.format("%d", value, True),1,'center',seconds=seconds)

            self.effect_repeater()

        def effect_repeater(self):
            value =self.value-self.display_repeats*self.divider
            timer = 0.3

            self.play_sound()
            self.game.switched_coils.drive('dropTargetFlasher',style='fast',time=timer)

            if self.display_repeats>0:
                self.delay(name='display_repeat',delay=timer,handler=self.display_text)
                self.display_repeating = True
                self.display_repeats-=1
            else:
                self.delay(name='cleanup',delay=2,handler=self.clear)


        def process(self):
            self.skillshot_in_progress = True
            self.game.set_player_stats('skillshot_in_progress',self.skillshot_in_progress)

            self.display_repeats = (self.value/self.divider)-1
            self.display_text()
            self.award_score()


        def other_switch(self):
            if not self.skillshot_in_progress:
                self.clear()

        def cancel(self):
            self.game.modes.remove(self)


        #switch handlers
        def sw_bottomDropTarget_active(self, sw):
            self.value+=self.top_value
            self.process()
            self.drops.progress(0)

            #return procgame.game.SwitchStop

        def sw_middleDropTarget_active(self, sw):
            self.value+=self.mid_value
            self.process()
            self.drops.progress(1)

            #return procgame.game.SwitchStop

        def sw_topDropTarget_active(self, sw):
            self.value+=self.bottom_value
            self.process()
            self.drops.progress(2)

            #return procgame.game.SwitchStop

        def sw_leftRebound_active(self,sw):
            self.other_switch()

        def sw_rightRebound_active(self,sw):
            self.other_switch()

        def sw_leftSlingshot_active(self,sw):
            self.other_switch()

        def sw_rightSlingshot_active(self,sw):
            self.other_switch()

        def sw_shooterLane_open_for_3s(self,sw):
            self.other_switch()



            