#Drops Mode

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

class Drops(game.Mode):

	def __init__(self, game, priority):
            super(Drops, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.drops')

            self.game.sound.register_sound('drop_target_hit', sound_path+"drop_target_hit.ogg")
            self.game.sound.register_sound('drop_target_completed', sound_path+"drop_target_completed.ogg")
            self.game.sound.register_sound('drop_target_sweep', sound_path+"drop_target_sweep.ogg")

            #set values
            self.base_value = 50000
            self.inc_value = 10000
            self.max_value = 100000


        def reset(self):
            self.flags = [False,False,False]
            self.hits =0
            self.value = self.base_value
            self.sweeping=False
            self.game.switched_coils.drive('dropTargetReset')


        def at_max(self):
            self.value = self.max_value

       
        def mode_started(self):
            self.reset()
            self.banks_completed = self.game.get_player_stats('drop_banks_completed')


        def mode_stopped(self):
            self.game.set_player_stats('drop_banks_completed',self.banks_completed)


        def display_completed_text(self, seconds=2, blink_rate=0.5, opaque=True, repeat=False, hold=False):
            self.game.score_display.set_text('drops completed'.upper(),0,'center',seconds=seconds)
            self.game.score_display.set_text(locale.format("%d", self.value, True),1,'center',seconds=2,blink_rate=blink_rate)

        def display_sweeping_text(self, seconds=2, blink_rate=0.5, opaque=True, repeat=False, hold=False):
            self.game.score_display.set_text('sweeping score'.upper(),0,'center',seconds=seconds)
            self.game.score_display.set_text(locale.format("%d", self.max_value, True)+'+'+locale.format("%d", self.value, True),1,'center',seconds=2,blink_rate=blink_rate)


        def update_count(self):
            
            self.hits+=1

            #update audit tracking
            self.game.game_data['Audits']['3-Bank Drop Targets Hits'] += 1


        def score(self,value):
            self.game.score(value)

         
        def check_sweeping(self):
            time = 0.2
            if self.game.switches.bottomDropTarget.time_since_change()<=time and self.game.switches.middleDropTarget.time_since_change()<=time and self.game.switches.topDropTarget.time_since_change()<=time:
                self.sweeping=True

                
        def progress(self,num):
            if self.flags[num]==False:
                self.flags[num]=True

                if not self.game.get_player_stats('skillshot_in_progress'):
                    #test for a completed set of drop targets
                    complete=True
                    for i in range(len(self.flags)):
                        if self.flags[i]==False:
                            complete=False

                    if complete:
                        timer=1
                        self.check_sweeping()
                        if self.sweeping:
                            timer=1.5
                            self.display_sweeping_text()
                            self.game.sound.play('drop_target_sweep')
                            self.sweeping=False

                        else:
                            timer=0.5
                            self.display_completed_text()
                            self.game.sound.play('drop_target_completed')

                        self.banks_completed+=1
                        self.game.switched_coils.drive('dropTargetFlasher',style='fast',time=timer)
                        self.delay(name='reset',delay=timer+0.5,handler=self.reset)
                    

                    else:
                        self.update_count()
                        self.game.sound.play('drop_target_hit')

                if self.value<=self.max_value:
                    self.value = self.base_value+(self.hits*self.inc_value)
                else:
                    self.value=self.max_value
                self.score(self.value)



        #switch handlers
        def sw_bottomDropTarget_active(self, sw):
            self.progress(0)

        def sw_middleDropTarget_active(self, sw):
            self.progress(1)

        def sw_topDropTarget_active(self, sw):
            self.progress(2)