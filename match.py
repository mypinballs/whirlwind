# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


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

class Match(game.Mode):

	def __init__(self, game, priority):
            super(Match, self).__init__(game, priority)

            self.log = logging.getLogger('testrig.match')

            self.match_layer = dmd.TextLayer(128/2, 10, self.game.fonts['23x12'] , "center", opaque=False)
            self.p1_layer = dmd.TextLayer(0, 0, self.game.fonts['6x6_bold'], "left", opaque=False)
            self.p2_layer = dmd.TextLayer(20, 0, self.game.fonts['6x6_bold'], "left", opaque=False)
            self.p3_layer = dmd.TextLayer(108, 0, self.game.fonts['6x6_bold'], "right", opaque=False)
            self.p4_layer = dmd.TextLayer(128, 0, self.game.fonts['6x6_bold'], "right", opaque=False)
            self.dmd_image = "dmd/blank.dmd"
            self.value_range = 9
            self.player_digits = [0,0,0,0]

            self.game.sound.register_sound('match_atmos', sound_path+"match_atmos.ogg")
            self.game.sound.register_sound('match', sound_path+"match.ogg")
            
            self.reset()


        def reset(self):
            pass


        def mode_started(self):
            self.generate_digits()
            self.generate_match()
            self.play_anim()


        def mode_stopped(self):
            #set the status
            self.game.system_status='game_over'
            
            #add the attact mode and play the see you tommorow sample
            self.game.modes.add(self.game.attract_mode)
           


        def play_anim(self):

            anim = dmd.Animation().load(game_path+self.dmd_image)
            self.bgnd_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,frame_time=2)
            self.animation_layer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,frame_time=2)
            self.animation_layer.composite_op = "blacksrc"
            #self.animation_layer.add_frame_listener(-1,self.clear)
            #set display layer
            self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.match_layer,self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer,self.animation_layer])
            #play sound
            self.game.sound.play('match')
            
            #setup end delay
            self.delay(name='end_delay', event_type=None, delay=5, handler=self.clear)
           

        def generate_match(self):
        #create the match value for comparison

            value = (random.randint(0, self.value_range))*10
            if value==0:
                display = "0"+str(value)
            else:
                display = str(value)



            #set text
            self.match_layer.set_text(display)


            #work out if player has matched digits and award as necassary
            for i in range(len(self.game.players)):
                if self.player_digits[i]==value:
                    self.player_layers[i].set_text(digit,blink_frames=10)
                    self.credits =  audits.display(self.game,'general','creditsCounter')
                    audits.update_counter(self.game,'credits',self.credits+1)
            

            #set clear time
            #self.delay(name='clear', event_type=None, delay=1.5, handler=self.clear)


        def generate_digits(self):
        #extract and display the last 2 score digits for each player

            self.player_layers=[self.p1_layer,self.p2_layer,self.p3_layer,self.p4_layer]

            for i in range(len(self.game.players)):
                score = self.game.players[i].score
                digit = str(score)[-2:]
                self.player_layers[i].set_text(digit)
                #set var for comparison
                self.player_digits[i]=digit
            

        def clear(self):
            self.layer = None
            self.game.modes.remove(self)
