# -------------------------
# Skyway Mode
# Controls Right Ramp and Eject Saucer
#
# Copyright (C) 2013 myPinballs, Orange Cloud Software Ltd
#
# -------------------------

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

class Skyway(game.Mode):

	def __init__(self, game, priority, mode1):
            super(Skyway, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.skyway')
            self.tornado =mode1

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)

            self.game.sound.register_sound('skyway_shot_made0', sound_path+"skyway_made1.ogg")
            self.game.sound.register_sound('skyway_shot_made1', sound_path+"skyway_made2.ogg")
            self.game.sound.register_sound('skyway_shot_made2', sound_path+"skyway_made3.ogg")
            self.game.sound.register_sound('skyway_shot_made3', sound_path+"skyway_made4.ogg")
            self.game.sound.register_sound('saucer_eject', sound_path+"saucer_eject.aiff")


            self.ramp_value_start = 50000
            self.ramp_value_boost = 10000
            self.ramp_value_extra = 20000
            self.ramp_value_limit = 100000

            self.lamps=['toll1','toll2','toll3','toll4','toll5','toll10','toll20','toll30']
            self.ramp_flashers =['rampTopFlasher','rampUMFlasher','rampLMFlasher','rampBottomFlasher']

            self.extra_ball_tolls = 10 # needs to be setting based and have more values

            self.reset()

        def reset(self):
            self.ramp_level = 0
            self.game.effects.drive_lamp('2tolls','off')

        def reset_lamps(self):
            for lamp in self.lamps:
                self.game.effects.drive_lamp(lamp,'off')

        def mode_started(self):
            self.skyway_tolls= self.game.get_player_stats('skyway_tolls')
            self.extra_ball_tolls = self.game.get_player_stats('skyway_eb_tolls')
            
        def mode_stopped(self):
            self.game.set_player_stats('skyway_tolls',self.skyway_tolls)
            self.game.set_player_stats('skyway_eb_tolls',self.extra_ball_tolls)


        def update_lamps(self):
            self.log.debug("Updating Skyway Lamps")

            full = self.skyway_tolls/5
            rem = self.skyway_tolls%5

            for i in range(rem):
                 self.game.effects.drive_lamp(self.lamps[i],'on')

            if full==1:
                self.game.effects.drive_lamp('toll5','on')
            elif full==2:
                self.game.effects.drive_lamp('toll10','on')
            elif full==3:
                self.game.effects.drive_lamp('toll5','on')
                self.game.effects.drive_lamp('toll10','on')
            elif full==4:
                self.game.effects.drive_lamp('toll20','on')

        def set_lamps(self):
            self.log.debug("Setting Skyway Lamps")

            full = self.skyway_tolls/5
            rem = self.skyway_tolls%5

            #turn off all lamps before setting the new values
            self.reset_lamps()

            for i in range(rem):
                 self.game.effects.drive_lamp(self.lamps[i],'smarton')

            if full==1:
                self.game.effects.drive_lamp('toll5','smarton')
            elif full==2:
                self.game.effects.drive_lamp('toll10','smarton')
            elif full==3:
                self.game.effects.drive_lamp('toll5','smarton')
                self.game.effects.drive_lamp('toll10','smarton')
            elif full==4:
                self.game.effects.drive_lamp('toll20','smarton')

        def play_animation(self, count, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_text(str(count)+' skyway tolls'.upper(),0,'center',seconds=2)
            self.game.score_display.set_text('extra ball at '.upper()+str(self.extra_ball_tolls),1,'center',seconds=2)

        def inc_tolls(self,num):
            self.toll(num)
            self.set_lamps()
            
            return self.skyway_tolls

        
        def progress(self):
            self.toll(1)
            if self.ramp_level>1:
                self.toll(1)
            self.play_sound()
            self.score()
            self.play_animation(self.skyway_tolls)
            self.strobe_ramp_flashers(0.2)
            self.set_lamps()
            self.combo()

            if self.skyway_tolls>=self.extra_ball_tolls:
                self.game.extra_ball.lit()
                self.extra_ball_tolls+=10


        def alt_progress(self):

            self.log.info('alt skyway progress')
            if not self.game.get_player_stats('multiball_running') and not self.game.get_player_stats('lock_lit'):
                self.toll(1)
                self.play_sound()
                self.score()
                self.play_animation(self.skyway_tolls)
                self.set_lamps()

                #update audits
                audits.record_value(self.game,'skywaySaucerMade')

            #queue eject
            self.delay(name='eject_ball',delay=2,handler=self.eject)


        def combo(self):
            self.ramp_level+=1
            self.game.effects.drive_lamp('2tolls','fast')
            self.tornado.set_level(self.ramp_level)

            self.cancel_delayed('skyway_reset')
            self.delay(name='skyway_reset',delay=5, handler=self.reset)

            #update audits
            audits.record_value(self.game,'skywayComboMade')


        def score(self):
            value = self.ramp_value_start*self.ramp_level*self.ramp_value_boost
            if value>self.ramp_value_limit:
                value=self.ramp_value_limit
            self.game.score(value)
            

        def play_sound(self):
            level = self.ramp_level
            if level>3:
                level=3
            self.game.sound.play('skyway_shot_made'+str(level))

            
        def strobe_ramp_flashers(self,time):
            timer = 0
            repeats = 3
            sequence=[]
            for j in range(repeats):
                sequence += self.ramp_flashers

            for i in range(len(sequence)):

                def flash(i,time,delay):
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='fast',time=time+0.6))

                flash(i,time,timer)
                timer+=time

        def toll(self,num):
            self.skyway_tolls+=num
            self.game.set_player_stats('skyway_tolls',self.skyway_tolls)

            #update audits
            audits.record_value(self.game,'skywayRampMade')

            
        def eject(self):
            self.game.sound.play('saucer_eject')
            self.game.switched_coils.drive('topEject')


        #switch handlers
        def sw_rightRampMadeTop_active(self, sw):
            self.progress()

        def sw_topRightEject_active_for_250ms(self, sw): #should this be where all saucer control is handled from? TODO:check this
            if not self.game.get_player_stats('quick_multiball_ready') and not self.game.get_player_stats('war_multiball_ready'):
                self.alt_progress()

