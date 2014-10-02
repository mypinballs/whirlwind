#Saucer Mode

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

class Tornado(game.Mode):

	def __init__(self, game, priority):
            super(Tornado, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.tornado')

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('tornado_level0', sound_path+"tornado_1.ogg")
            self.game.sound.register_sound('tornado_level1', sound_path+"tornado_2.ogg")
            self.game.sound.register_sound('tornado_level2', sound_path+"tornado_3.ogg")
            self.game.sound.register_sound('tornado_level3', sound_path+"tornado_4.ogg")
            self.game.sound.register_sound('tornado_level4', sound_path+"tornado_4.ogg")

            self.lamps=['topDrop50k','topDrop75k','topDrop100k','topDrop150k','topDropQuickMB']
            self.score_value=[50000,75000,100000,150000,200000]

            self.timeout_time = 10 # add a setting for this
            
             #defs for mode linkup
            self.quick_multiball = None

            

        def config_level(self):
            self.difficulty = self.game.user_settings['Feature']['Tornado Difficulty']
            if self.difficulty=='Easy':
                self.level = 3
            elif self.difficulty=='Medium':
                self.level = 1
            elif self.difficulty=='Hard':
                self.level = 0


        def reset(self):
            self.qm_activated = False # flag that only allows qm from here once
            self.config_level()
            self.reset_target()
            
            
        def reset_target(self):
            if self.game.switches.topSingleDropTarget.is_active():
                self.game.switched_coils.drive('singleDropTargetReset')


        def timeout(self):
            self.game.effects.drive_lamp(self.lamps[self.level-1],'timeout',self.timeout_time)
            self.level-=1
            if self.level>0:
                self.delay(name='start_timeout',delay=self.timeout_time, handler=self.timeout)


        def set_level(self,num):
            self.level = num
            self.set_lamps()


        def update_lamps(self):
            for i in range(self.level):
                self.game.effects.drive_lamp(self.lamps[i],'on')

        def set_lamps(self):
            for i in range(self.level):
                self.game.effects.clear_lamp_timers(self.lamps[i])
                self.game.effects.drive_lamp(self.lamps[i],'smarton')

            self.cancel_delayed('start_timeout')
            self.delay(name='start_timeout',delay=1, handler=self.timeout)

            
        def mode_started(self):
            self.hits = self.game.get_player_stats('tornados_collected')
            self.level = self.game.get_player_stats('tornado_level')
            
            self.reset()
            
        def mode_stopped(self):
            self.game.set_player_stats('tornados_collected',self.hits)
            self.game.set_player_stats('tornado_level',self.level)

        def update_count(self):         
            self.hits+=1

            #update audits
            audits.record_value(self.game,'tornadoTargetHit')
    
        def score(self,value):
            self.game.score(value)

        def hit(self):
            self.log.info('Tornado Level is:%s',self.level)
            self.update_count()
            self.score(self.score_value[self.level])
            self.game.sound.play('tornado_level'+str(self.level))
            self.delay(name='topdropreset',delay=1,handler=lambda:self.game.switched_coils.drive('singleDropTargetReset'))
            
            #quick multiball option
            if self.level==4 and not self.qm_activated:
                self.qm_activated=True
                self.quick_multiball()
                

            

        def sw_topSingleDropTarget_active_for_250ms(self, sw):
            if self.game.ball>0:
                self.hit()
