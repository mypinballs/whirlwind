import procgame
from procgame import *
import locale
import logging


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Bonus(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
		super(Bonus, self).__init__(game, priority)

                self.log = logging.getLogger('whirlwind.bonus')

                self.game.sound.register_music('bonus', music_path+"bonus.aiff")
                self.game.sound.register_sound('bonus_features', sound_path+"bonus_features.aiff")
                self.game.sound.register_sound('bonus_multiplier', sound_path+"bonus_multiplier.aiff")
                self.game.sound.register_sound('bonus_total', sound_path+"bonus_total.aiff")
                self.game.sound.register_sound('bonus_end', sound_path+"bonus_end.aiff")

                self.bonus_counter = 0
                self.mode_counter =0
                self.mode_total = 0
		self.delay_time = 1.6
                self.base_value = 1000
                self.total_value = 0
                self.remaining = 0
                self.toll_value = 2000


	def mode_started(self):
		# Disable the flippers
		self.game.enable_flippers(enable=False)
                self.log.debug("Bonus Mode Started")


	def mode_stopped(self):
		# Enable the flippers
		self.game.enable_flippers(enable=True)
                self.game.sound.stop_music()
                self.log.debug("Debug, Bonus Mode Ended")


        def get_bonus_value(self):
            skyways = self.game.get_player_stats('skyway_tolls') * 2000
            return self.base_value+skyways


        def get_bonus_x(self):
            bonus_x = self.game.get_player_stats('bonus_x')
            return bonus_x
        

        def calculate(self,callback):
            #self.game.sound.play_music('bonus', loops=1)
	    self.callback = callback
            self.total_value = self.game.get_player_stats('skyway_tolls') * self.toll_value * self.game.get_player_stats('bonus_x')
            self.remaining = self.total_value
            self.skyways()


        def skyways(self):
            self.game.score_display.set_text(str(self.game.get_player_stats('skyway_tolls'))+' skyway tolls'.upper(),0,'center',seconds=self.delay_time)
            self.game.score_display.set_text(locale.format("%d", self.game.get_player_stats('skyway_tolls') * self.toll_value, True),1,'center',seconds=self.delay_time)

            self.game.sound.play('bonus_features')
            
            self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.multiplier)


        def multiplier(self):
            self.game.score_display.set_text('x'+str(self.game.get_player_stats('bonus_x')).upper(),0,'center',seconds=self.delay_time)
            self.game.score_display.set_text(locale.format("%d", self.total_value, True),1,'center',seconds=self.delay_time)

            self.game.sound.play('bonus_multiplier')

            self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.total)


        def total(self):
            self.game.score_display.restore()
            self.game.sound.play_music('bonus', loops=1)
            self.add_score()


        def add_score(self):
            timer = 0.05
            #update the display
            self.game.score_display.set_text(locale.format("%d", self.remaining, True),1,'center',seconds=self.delay_time)

            #add bonus score and update remaining var
            self.game.score(2137) # this should update the player score in question
            self.remaining-=2137

            if self.remaining>0:
                self.delay(name='update', event_type=None, delay=timer, handler=self.add_score)
            else:
                self.finish()


        def finish(self):
            self.game.sound.fadeout_music()
            self.game.sound.play('bonus_end')
            self.callback()


	def sw_flipperLwL_active(self, sw):
		if self.game.switches.flipperLwR.is_active():
			self.game.score(self.remaining)
                        self.finish()

	def sw_flipperLwR_active(self, sw):
		if self.game.switches.flipperLwL.is_active():
			self.game.score(self.remaining)
                        self.finish()

