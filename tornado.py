#Saucer Mode

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

class Tornado(game.Mode):

	def __init__(self, game, priority):
            super(Tornado, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.tornado')

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('tornado_level1', sound_path+"tornado_1.ogg")
            self.game.sound.register_sound('tornado_level2', sound_path+"tornado_2.ogg")
            self.game.sound.register_sound('tornado_level3', sound_path+"tornado_3.ogg")
            self.game.sound.register_sound('tornado_level4', sound_path+"tornado_4.ogg")

            self.lamps=['topDrop50k','topDrop75k','topDrop100k','topDrop150k','topDropQuickMB','topDropEB']
            self.score_value=[50000,75000,100000,150000,200000,200000]

            self.timeout_time = 10 # add a setting for this

            self.reset()


        def reset(self):
            self.level =0
            self.game.switched_coils.drive('singleDropTargetReset')

        def timeout(self):
            self.game.effects.drive_lamp(self.lamps[self.level],'timeout',self.timeout_time)
            level = self.level-1
            if self.level>0:
                self.delay(name='start_timeout',delay=self.timeout_time, handler=self.set_level,param=level)


        def set_level(self,num):
            self.level = num
            self.set_lamps()

        def update_lamps(self):
            for i in range(self.level):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def set_lamps(self):
            for i in range(self.level):
                self.game.effects.drive_lamp(self.lamps[i],'smarton')

            self.delay(name='start_timeout',delay=1, handler=self.timeout)
            
        def mode_started(self):
            self.tornado_hits = self.game.get_player_stats('tornados_collected')
            self.tornado_level = self.game.get_player_stats('tornado_level')
            
        def mode_stopped(self):
            self.game.set_player_stats('tornados_collected',self.tornado_hits)
            self.game.set_player_stats('tornado_level',self.tornado_level)

        def update_count(self):
            
            self.tornado_hits+=1

            #update audit tracking
            self.game.game_data['Audits']['Tornados'] += 1
    
        def score(self,value):
            self.game.score(value)

        def hit(self):
            self.update_count()
            self.score(self.score_value[self.level])
            self.game.sound.play('tornado_level'+str(self.level))
            self.delay(name='topdropreset',delay=1,handler=lambda:self.game.switched_coils.drive('singleDropTargetReset'))

        def sw_topSingleDropTarget_active_for_250ms(self, sw):
            if self.game.ball>0:
                self.hit()
