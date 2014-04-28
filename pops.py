# Pop Bumpers Mode


import procgame
import locale
import random
import logging
import audits
from procgame import *
from utility import boolean_format


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"


class Pops(game.Mode):

	def __init__(self, game, priority):
            super(Pops, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.pops')

            self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('pop1', sound_path+"pop_1.ogg")
            self.game.sound.register_sound('pop2', sound_path+"pop_2.ogg")
            self.game.sound.register_sound('pop3', sound_path+"pop_3.ogg")
            self.game.sound.register_sound('pop4', sound_path+"pop_4.ogg")
            self.game.sound.register_sound('pop5', sound_path+"pop_5.ogg")
            self.game.sound.register_sound('super1', sound_path+"super_pop_1.ogg")
            self.game.sound.register_sound('super2', sound_path+"super_pop_2.ogg")
            self.game.sound.register_sound('super3', sound_path+"super_pop_3.ogg")
            self.game.sound.register_sound('super4', sound_path+"super_pop_4.ogg")
            self.game.sound.register_sound('super5', sound_path+"super_pop_5.ogg")
            
            self.game.sound.register_sound('pop_lit', sound_path+"pop_lit.ogg")
            self.game.sound.register_sound('pop_max', sound_path+"pop_max.ogg")



            self.lamps = ['lowerLeftJet','lowerRightJet','lowerTopJet','upperBottomJet','upperLeftJet','upperRightJet']
            self.super_pops_default = int(self.game.user_settings['Feature']['Super Jets Start'])
            self.super_pops_enabled = boolean_format(self.game.user_settings['Feature']['Super Jets Enabled'])

            self.spot_pop = 0
            self.reset()

        def reset(self): #reset the following at any time from call
           
            self.super_pops_raise = 25
            self.super_score = 10000
            self.base_score = 1000
            self.center_target_score = 5000
            self.pops_at_max=False
            self.animation_status='ready'
            

        def mode_started(self):
            self.flags = self.game.get_player_stats('pop_flags')

            self.lower_super_pops_collected = self.game.get_player_stats('lower_super_pops_collected')
            self.lower_super_pops_level =self.game.get_player_stats('lower_super_pops_level')
            self.lower_super_pops_required =  self.super_pops_default + (self.super_pops_raise*self.lower_super_pops_level)
            
            self.upper_super_pops_collected = self.game.get_player_stats('upper_super_pops_collected')
            self.upper_super_pops_level =self.game.get_player_stats('upper_super_pops_level')
            self.upper_super_pops_required =  self.super_pops_default + (self.super_pops_raise*self.upper_super_pops_level)

        def mode_stopped(self):
            self.game.set_player_stats('pop_flags',self.flags)

            self.game.set_player_stats('lower_super_pops_collected',self.lower_super_pops_collected)
            self.game.set_player_stats('upper_super_pops_collected',self.upper_super_pops_collected)

            if self.lower_super_pops_required==0:
                self.lower_super_pops_level+=1
            self.game.set_player_stats('lower_super_pops_level',self.lower_super_pops_level)

            if self.upper_super_pops_required==0:
                self.upper_super_pops_level+=1
            self.game.set_player_stats('upper_super_pops_level',self.upper_super_pops_level)


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                self.game.effects.drive_lamp(self.lamps[i],'off')


        def update_lamps(self):
            for i in range(len(self.lamps)):
                if self.flags[i]==1:
                    self.game.effects.drive_lamp(self.lamps[i],'on')
                elif self.flags[i]==2:
                    self.game.effects.drive_lamp(self.lamps[i],'fast')

        def set_lamps(self,num):
            if self.flags[num]==1:
                self.game.effects.drive_lamp(self.lamps[num],'on')
            elif self.flags[num]==2:
                self.game.effects.drive_lamp(self.lamps[num],'fast')
                

        def play_sound(self):

            list=["pop1","pop2","pop3","pop4","pop5"]
            super_list =["super1","super2","super3","super4","super5"]

            if self.lower_super_pops_required==0 or self.upper_super_pops_required==0:
                i= random.randint(0, len(super_list)-1)
            else:
                i= random.randint(0, len(list)-1)

            self.game.sound.play(list[i])


        def play_animation(self, count,set, opaque=True, repeat=False, hold=False, frame_time=3):
            if set==0:
                name='low'
            elif set==1:
                name='high'

            self.game.score_display.set_text(str(count)+' hits for'.upper(),0,'center',seconds=2)
            self.game.score_display.set_text('super '+name+' jets'.upper(),1,'center',seconds=2)


        def play_super_animation(self,count,set,opaque=False, repeat=False, hold=False, frame_time=3):
            if set==0:
                name='low'
                self.game.switched_coils.drive("rampTopFlasher",style='slow',cycle=1)
            elif set==1:
                name='high'
                self.game.switched_coils.drive("rampLMFlasher",style='slow',cycle=1)

            self.game.score_display.set_text('super '+name+' jets'.upper(),0,'center')
            score = count * self.super_score
            self.game.score_display.set_text(locale.format("%d",score,True),1,'center',blink_rate=0.5)

           
        def update_count(self,set):
            if set==0:
                if self.super_pops_enabled:
                    if self.lower_super_pops_required>0:
                        self.lower_super_pops_required -=1
                        self.play_animation(self.lower_super_pops_required,set)
                    else:
                        self.lower_super_pops_collected+=1
                        self.play_super_animation(self.lower_super_pops_collected,set)

                        #update audits
                        audits.record_value(self.game,'lowerSuperPopCollected')

                self.game.switched_coils.drive("rampLMFlasher",style='fast',time=0.5)

                

            elif set==1:
                if self.super_pops_enabled:
                    if self.upper_super_pops_required>0:
                        self.upper_super_pops_required -=1
                        self.play_animation(self.upper_super_pops_required,set)
                    else:
                        self.upper_super_pops_collected+=1
                        self.play_super_animation(self.upper_super_pops_collected,set)

                        #update audits
                        audits.record_value(self.game,'upperSuperPopCollected')

                self.game.switched_coils.drive("rampTopFlasher",style='fast',time=0.5)
                    
    
        def pops_score(self,num):
            value  = (self.flags[num]*self.flags[num])+1

            if self.lower_super_pops_required==0 or self.upper_super_pops_required==0:
                self.game.score(self.super_score+self.super_score*value)
            else:
                self.game.score(self.base_score*value)


        def check_pops_max(self): #check if we have maxed all pops?
            value=0
            for num in self.flags:
                value+=num

            if value==2*len(self.flags):
                self.pops_at_max=True
                self.center_target_score = 100000
                self.game.effects.drive_lamp('middleStandup','smarton')

        def progress(self):

            #update the pop flags and lamps
            if self.pops_at_max==False:
                value =self.flags[self.spot_pop]
                if value<2:
                    self.flags[self.spot_pop]+=1
                    self.game.sound.play('pop_lit')
                    self.set_lamps(self.spot_pop)
                else:
                    self.game.sound.play('pop_max')
                    self.check_pops_max()
            
                #wrap the flag count if needed
                self.spot_pop+=1
                if self.spot_pop==len(self.flags):
                    self.spot_pop = 0

            #score
            self.game.score( self.center_target_score)


        def max_lower_pops(self):
            for i in range(0,3):
                self.flags[i]=2

            self.update_lamps()
            self.check_pops_max()


        def max_upper_pops(self):
            for i in range(3,6):
                self.flags[i]=2

            self.update_lamps()
            self.check_pops_max()


        def sw_lowerLeftJet_active(self, sw):
            self.update_count(0)

            self.pops_score(0)
            self.play_sound()
           

        def sw_lowerRightJet_active(self, sw):
            self.update_count(0)

            self.pops_score(1)
            self.play_sound()
            

        def sw_lowerTopJet_active(self, sw):
            self.update_count(0)

            self.pops_score(2)
            self.play_sound()

          
        def sw_upperBottomJet_active(self, sw):
            self.update_count(1)

            self.pops_score(3)
            self.play_sound()


        def sw_upperLeftJet_active(self, sw):
            self.update_count(1)

            self.pops_score(4)
            self.play_sound()


        def sw_upperRightJet_active(self, sw):
            self.update_count(1)

            self.pops_score(5)
            self.play_sound()


        def sw_middleStandup_active(self,sw):
                self.progress()


