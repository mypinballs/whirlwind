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
import audits
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
            self.game.sound.register_sound('hurryup_start_speech', speech_path+"head_for_the_cellar.ogg")
            self.game.sound.register_sound('hurryup_collected_speech', speech_path+"youall_come_back_now.ogg")
            self.game.sound.register_sound('cellar_award_speech', speech_path+"well_lucky_here.ogg")
            self.game.sound.register_sound('cellar_eject', sound_path+"cellar_eject.ogg")
            self.game.sound.register_sound('cellar_eject_kick', sound_path+"cellar_eject_kick.aiff")
            self.game.sound.register_sound('door_knock', sound_path+"5knocks2.ogg")
            self.game.sound.register_sound('door_knock', sound_path+"5knocks1.ogg")
            self.game.sound.register_sound('door_knock', sound_path+"3knocks.ogg")

            self.reset()

            self.awards_text_top = ['Upper Super Jets','Big Points','Extra Ball Lit','3-Bank','Light','Lite','Lower Super Jets']
            self.awards_text_bottom = ['100K per pop','500K','','100K','Quick Multiball','Million','100K per pop']
            self.lamps = ['scUpperJetsOn','sc500k','scExtraBall','sc3Bank100k','scQuickMultiball','scMillion','scLowerJetsOn']

            #defs for callback linkup
            self.lite_million = None
            self.quick_multiball = None
            self.war_multiball = None
            self.drops = None
            self.lower_pops = None
            self.upper_pops = None

        def reset(self):
            self.score_value_boost = 1000
            self.score_value_start = 5000
            self.super_door_score = 500000
            self.big_points = 250000
            self.cellar_lit = False
            self.skyway_open = True
            self.award_id = 0
            self.secret_mode = False

            self.hurryup_reset2()

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


        def cellar_award_part1(self):
            wait =self.game.sound.play_voice('cellar_award_speech')

            self.delay(name='award_delay',delay=wait+0.2, handler=self.cellar_award_part2)


        def cellar_award_part2(self):
            if self.award_id==0:
                self.upper_pops()
            elif self.award_id==1:
                self.score(self.big_points)
            elif self.award_id==2:
                self.game.extra_ball.lit()
                audits.record_value(self.game,'cellarExtraBall')
            elif self.award_id==3:
                self.drops()
            elif self.award_id==4:
                if self.secret_mode:
                    self.war_multiball()
                    self.secret_mode_unlocked = False
                else:
                    self.quick_multiball()
                    audits.record_value(self.game,'cellarQuickMultiball')
            elif self.award_id==5:
                self.lite_million() # populated by 'callback' linkup in base.py
            elif self.award_id==6:
                 self.lower_pops()

            self.game.score_display.set_text(self.awards_text_top[self.award_id].upper(),0,'center',seconds=2)
            self.game.score_display.set_text(self.awards_text_bottom[self.award_id].upper(),1,'center',seconds=2)

            self.delay(name='eject_delay',delay=2, handler=self.eject)

            self.cellar_lit = False
            self.update_lamps()

            #update audits
            audits.record_value(self.game,'cellarAward')


        def change_award(self):
            num = random.randint(0,6)
            self.award_id = num
            self.log.debug('Cellar Award Now: %s',self.lamps[self.award_id])
            self.update_lamps()


        def lite_cellar(self,num=0):
            self.cellar_lit = True
            self.game.effects.clear_lamp_timers('rightCellarSign')
            self.game.effects.drive_lamp('rightCellarSign','smarton')
            if num>0:
                self.game.effects.drive_lamp('rightCellarSign','timeout',num)
                self.cancel_delayed('timeout_delay')
                self.delay(name='timeout_delay',delay=num, handler=self.reset)


        def display_hurryup_text(self):
            self.game.score_display.set_text('Cellar Hurryup'.upper(),0,justify='center',blink_rate=0.2)


        def display_hurryup_countdown_text(self):
            self.game.score_display.set_text(locale.format("%d", self.hurryup_value, True),1,justify='center')

            if self.hurryup_value>self.hurryup_base:
                self.hurryup_value-=1530
            else:
                self.hurryup_value=self.hurryup_base

            self.delay(name='update_hurryup_display', event_type=None, delay=0.1, handler=self.display_hurryup_countdown_text)


        def hurryup(self):
            self.hurryup_lit = True
            self.game.sound.play_voice('hurryup_start_speech')
            self.game.effects.drive_lamp('leftCellarSign','fast')

            self.display_hurryup_text()
            self.display_hurryup_countdown_text()

            self.delay(name='cancel_hurryup', event_type=None, delay=self.hurryup_timer, handler=self.hurryup_timeout)


        def hurryup_timeout(self):
            self.cancel_delayed('update_hurryup_display')
            self.hurryup_reset1()
            self.delay(name='cancel_hurryup', event_type=None, delay=self.hurryup_grace_time, handler=self.hurryup_reset2)


        def hurryup_collected(self):
            time=2
            self.cancel_delayed('update_hurryup_display')
            self.game.score_display.set_text('Cellar HurryUp',0,'center',seconds=time)
            self.game.score_display.set_text(locale.format("%d", self.hurryup_value, True),1,justify='center',blink_rate=0.2,seconds=2)

            self.game.sound.play_voice('hurryup_collected_speech')
            
            self.game.score(self.hurryup_value)

            self.delay(name='cleanup_hurryup', event_type=None, delay=time, handler=self.hurryup_reset1)
            self.delay(name='cleanup_hurryup', event_type=None, delay=time, handler=self.hurryup_reset2)
            self.delay(name='eject_delay',delay=time, handler=self.eject)


        def hurryup_reset1(self):
            self.game.effects.drive_lamp('leftCellarSign','off')
            self.game.score_display.restore()

        def hurryup_reset2(self):
            self.hurryup_lit = False
            self.hurryup_timer = 15
            self.hurryup_value= 1000000
            self.hurryup_base= 25000
            self.hurryup_grace_time=2
           

        def update_count(self):
            
            self.cellar_visits+=1

            #update audit tracking
            audits.record_value(self.game,'cellarVisit')
    
        def score(self,value):
            self.game.score(value)


        def eject(self):
            self.score(self.score_value_start)
            timer = self.game.sound.play('cellar_eject')
            self.game.switched_coils.drive('rampBottomFlasher','fast',time=timer-0.2)#1.2
            self.delay(name='coil_delay', event_type=None, delay=timer, handler=self.eject_kick)

        def eject_kick(self):
            self.game.sound.play('cellar_eject_kick')
            self.game.switched_coils.drive('rampBottomFlasher','super',time=0.2)
            self.game.coils.cellarKickout.pulse()


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
            wait=0.1

            #set the secret mode flag?
            if self.game.switches.flipperLwR.is_active(0.5):
                self.secret_mode = True
            else:
                 self.secret_mode = False

            self.log.debug('Cellar Lit Status:%s',self.cellar_lit)
            self.log.debug('Secret Mode Enabled: %s',self.secret_mode)

            if not self.game.get_player_stats('multiball_running') and not self.game.get_player_stats('quick_multiball_running') and not self.game.get_player_stats('qm_lock_lit') and not self.game.get_player_stats('war_multiball_running') and not self.game.get_player_stats('war_lock_lit'):
                if not self.game.get_player_stats('lock_lit') and not self.game.get_player_stats('qm_lock_lit'):
                    self.toggle_skyway_entrance()

                if self.hurryup_lit: #check for hurry up made
                    self.hurryup_collected()
                elif self.cellar_lit and self.game.switches.rightCellar.time_since_change()<=1.2:
                    wait =self.game.sound.play('door_knock')
                    self.delay(name='award_delay',delay=wait+0.2, handler=self.cellar_award_part1)
                else:
                    num = random.randint(0,10)
                    if num>3 and not self.game.get_player_stats('lock_lit'): #only play speech 'sometimes' and not when lock it lit
                        wait=self.game.sound.play_voice('cellar_unlit')
                    self.delay(name='eject_delay',delay=wait, handler=self.eject)
            else:
                if self.game.get_player_stats('multiball_running') or self.game.get_player_stats('quick_multiball_running') or self.game.get_player_stats('war_multiball_running'): #add extra wait before kickout when multiballs running
                    wait=wait+6
                    self.game.effects.drive_lamp('leftCellarSign','timeout',wait)

                self.delay(name='eject_delay',delay=wait, handler=self.eject)

            


        def sw_rightInlane_active(self, sw):
            if not self.game.get_player_stats('multiball_running') and not self.hurryup_lit:
                self.lite_cellar(20)


        def sw_spinner_active(self, sw):
            self.change_award()
            
