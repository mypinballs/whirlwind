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
            self.game.sound.register_sound('door_knock', sound_path+"5knocks2.ogg")

            self.reset()

            self.awards_text_top = ['Upper Super Jets','Big Points','Extra Ball Lit','3-Bank','Super Door Score','Lite Million','Lower Super Jets']
            self.awards_text_bottom = ['100K per pop','250K','','100K','500K','','100K per pop']
            self.lamps = ['scUpperJetsOn','sc250k','scExtraBall','sc3Bank100k','sc500k','scMillion','scLowerJetsOn']

        def reset(self):
            self.score_value_boost = 1000
            self.score_value_start = 5000
            self.super_door_score = 500000
            self.big_points = 250000
            self.cellar_lit = False
            self.skyway_open = True
            self.award_id = 0

        def timeout(self):
            self.reset()
            self.update_lamps()

        def update_lamps(self):
            if self.cellar_lit:
                self.game.effects.drive_lamp('rightCellarSign','on')
            else:
                self.game.effects.drive_lamp('rightCellarSign','off')

            for lamp in self.lamps:
                self.game.effects.drive_lamp(lamp,'off')
            self.game.effects.drive_lamp(self.lamps[self.award_id],'medium')

        def mode_started(self):
            self.cellar_visits = self.game.get_player_stats('cellar_visits')
            self.change_award()
            
        def mode_stopped(self):
            self.game.set_player_stats('cellar_visits',self.cellar_visits)

        def cellar_award(self):
            if self.award_id==0:
                pass
            elif self.award_id==1:
                self.score(self.big_points)
            elif self.award_id==2:
                pass
                #self.game.extra_ball.lit()
            elif self.award_id==3:
                pass
            elif self.award_id==4:
                self.score(self.super_door_score)
            elif self.award_id==5:
                pass
            elif self.award_id==6:
                pass

            self.game.score_display.set_text(self.awards_text_top[self.award_id],0,'center',seconds=2)
            self.game.score_display.set_text(self.awards_text_bottom[self.award_id],1,'center',seconds=2)

            self.delay(name='eject_delay',delay=2, handler=self.eject)

        def change_award(self):
            num = random.randint(0,6)
            self.award_id = num
            self.update_lamps()

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
        
        def sw_leftCellar_active_for_250ms(self, sw):
            self.update_count()
            wait=0

            if not self.game.get_player_stats('multiball_running'):
                if not self.game.get_player_stats('lock_lit'):
                    self.toggle_skyway_entrance()
            
                if self.cellar_lit:
                    wait =self.game.sound.play('door_knock')
                    self.delay(name='award_delay',delay=wait, handler=self.cellar_award)
                    
                else:
                    
                    num = random.randint(0,10)
                    if num>3 and not self.game.get_player_stats('lock_lit'): #only play speech 'sometimes' and not when lock it lit
                        wait=self.game.sound.play_voice('cellar_unlit')
                    self.delay(name='eject_delay',delay=wait, handler=self.eject)
            else:
                 self.delay(name='eject_delay',delay=wait, handler=self.eject)


        def sw_rightInlane_active(self, sw):
            if not self.game.get_player_stats('multiball_running'):
                self.lite_cellar(20)


        def sw_spinner_active(self, sw):
            self.change_award()