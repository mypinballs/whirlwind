# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
import audits
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Extra_Ball(game.Mode):

	def __init__(self, game,priority):
            super(Extra_Ball, self).__init__(game, priority)

            self.game.sound.register_sound('extra_ball_collected', sound_path+"extra_ball_lit_ff.ogg")
            self.game.sound.register_sound('extra_ball_lit', sound_path+"extra_ball_lit_ff.ogg")
            self.game.sound.register_sound('extra_ball_speech', speech_path+"extra_ball_speech.ogg")


        def display(self, top, bottom, seconds, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_transition_reveal(text=top.upper(),row=0,seconds=seconds)
            self.game.score_display.set_transition_reveal(text=bottom.upper(),row=1,seconds=seconds)

        def schedule_all_lamps(self, enable=True, timer=2):
		# Start the lamps doing a crazy rotating sequence:
		schedules = [0x55555555, 0xaaaaaaaa]
		for index, lamp in enumerate(sorted(self.game.lamps, key=lambda lamp: lamp.number)):
			if enable:
				sched = schedules[index%len(schedules)]
				lamp.schedule(schedule=sched, cycle_seconds=timer, now=False)
			else:
				lamp.disable()
                                
                #self.delay(name='disable_eb_lamp_show',delay=timer,handler=lambda:self.schedule_all_lamps(enable=False))

                
        def update_lamps(self):
            if self.game.get_player_stats("extra_ball_status")==1:
                self.game.effects.drive_lamp('scExtraBall','on')
            elif self.game.get_player_stats("extra_ball_status")==2:
                self.game.effects.drive_lamp('shootAgain','on')
                
            
        def collect(self):
            self.log.info("Extra Ball Collected")
            self.game.set_player_stats("extra_ball_status",2)
            self.display(top='Extra Ball',bottom='',seconds=3)
            self.game.sound.play('extra_ball_collected')
            #self.game.sound.play_voice('extra_ball_speech')
            self.game.effects.drive_lamp('scExtraBall','off')
            self.game.effects.drive_lamp('shootAgain','smarton')
            self.game.extra_ball_count()

            audits.record_value(self.game,'extraBallAwarded')


        def lit(self):
            timer=3
            self.game.set_player_stats("extra_ball_status",1)
            self.display(top='Extra Ball',bottom='Lit',seconds=timer)
            self.game.sound.play('extra_ball_lit')
            self.schedule_all_lamps(timer-1)
            self.delay(delay=timer,handler=self.lit_finish)


        def lit_finish(self):
            self.game.update_lamps()
            self.game.effects.drive_lamp('scExtraBall','smarton')
            audits.record_value(self.game,'extraBallLit')
        

                
