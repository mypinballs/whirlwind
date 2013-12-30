# -------------------------
# Cellar Mode
#
# Awards items from the backbox list
# Controls Cellar Scoop and Skyway Ramp Entrance
# Active item is changed by Spinner
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

class Cellar(game.Mode):

	def __init__(self, game, priority):
            super(Cellar, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.cellar')

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('cellar_unlit', speech_path+"go_away.ogg")
            self.game.sound.register_sound('cellar_unlit', speech_path+"no_storm_now.ogg")
            self.game.sound.register_sound('cellar_unlit', speech_path+"now_get_out.ogg")
            self.game.sound.register_sound('cellar_eject', sound_path+"cellar_eject.ogg")

            self.reset()

            self.awards_text_top = ['SUPER DOOR SCORE']
            self.awards_text_bottom = ['500K']

        def reset(self):
            self.score_value_boost = 1000
            self.score_value_start = 5000
            self.super_door_score = 500000
            self.cellar_lit = False
            self.skyway_open = True

        def timeout(self):
            self.reset()
            self.update_lamps()

        def update_lamps(self):
            if self.cellar_lit:
                self.game.effects.drive_lamp('rightCellarSign','on')
            else:
                self.game.effects.drive_lamp('rightCellarSign','off')

        def mode_started(self):
            self.cellar_visits = self.game.get_player_stats('cellar_visits')
            
        def mode_stopped(self):
            self.game.set_player_stats('cellar_visits',self.cellar_visits)

        def cellar_award(self):
            award = 0 #temp fix
            if award==0:
                self.score(self.super_door_score)

            self.game.score_display.set_text(self.awards_text_top[award],0,'center',seconds=2)
            self.game.score_display.set_text(self.awards_text_bottom[award],1,'center',seconds=2)

            self.delay(name='eject_delay',delay=4, handler=self.eject)

        def lite_cellar(self,num=0):
            self.cellar_lit = True
            self.game.effects.drive_lamp('rightCellarSign','smarton')
            if num>0:
                self.game.effects.drive_lamp('rightCellarSign','timeout',num)
                self.delay(name='timeout_delay',delay=num, handler=self.reset)

        def update_count(self):
            
            self.cellar_visits+=1

            #update audit tracking
            self.game.game_data['Audits']['Cellar Visits'] += 1
    
        def score(self,value):
            self.game.score(value)


        def eject(self):
            self.score(self.score_value_start)
            self.game.sound.play('cellar_eject')
            self.game.switched_coils.drive('rampBottomFlasher','fast',time=1.2)
            self.delay(name='coil_delay', event_type=None, delay=1, handler=self.game.coils.cellarKickout.pulse)


        def toggle_skyway_entrance(self):
            if not self.game.get_player_stats('multiball_running'):
                if self.skyway_open:
                    self.game.switched_coils.drive('rampLifter')
                    self.skyway_open = False
                else:
                    self.game.coils['rampDown'].pulse()
                    self.skyway_open = True


        #switch handlers
        #-----------------------
        
        def sw_leftCellar_active(self, sw):
            self.update_count()
            wait=0

            if not self.game.get_player_stats('multiball_running'):
                if not self.game.get_player_stats('lock_lit'):
                    self.toggle_skyway_entrance()
            
                if self.cellar_lit:
                    self.cellar_award()
                else:
                    
                    num = random.randint(0,10)
                    if num>3: #only play speech 'sometimes'
                        wait=self.game.sound.play_voice('cellar_unlit')
                    self.delay(name='eject_delay',delay=wait, handler=self.eject)
            else:
                 self.delay(name='eject_delay',delay=wait, handler=self.eject)


        def sw_rightInlane_active(self, sw):
            if not self.game.get_player_stats('multiball_running'):
                self.lite_cellar(20)


        def sw_spinner_active(self, sw):
            pass