# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Tilt(game.Mode):

	def __init__(self, game,priority):
            super(Tilt, self).__init__(game, priority)

            self.text_layer = dmd.TextLayer(128/2, 10, self.game.fonts['num_09Bx7'], "center", opaque=True)

            self.game.sound.register_sound('tilt', sound_path+"tilt.ogg")
            self.game.sound.register_sound('tilt_warning', sound_path+"tilt_warning.ogg")

            self.reset()

        def reset(self):
            self.status = 0
            self.times_warned = 0;

        def status(self):
            if self.status==0:
                return False
            elif self.status==1:
                return True

	def tilt(self):

                #check if already in a tilt state
		if self.status == 0:

                        #set status
                        self.status = 1

			#update display
                        self.text_layer.set_text("TILT",blink_frames=20)
			self.layer = self.text_layer

                        #play sound
                        self.game.sound.play('tilt')

			#turn off flippers
			self.game.enable_flippers(enable=False)

			# Make sure ball won't be saved when it drains.
			self.game.ball_save.disable()

			# Make sure the ball search won't run while ball is draining.
			self.game.ball_search.disable()

			#turn off all lamps
			for lamp in self.game.lamps:
				lamp.disable()

			#check for stuck balls
#			if self.game.switches.shooterLane.is_active():
#				self.game.coils.ballLaunch.pulse(50)

        def warning(self):
            self.times_warned += 1

            #update display
            time=2
            self.text_layer.set_text("WARNING",blink_frames=5,seconds=time)
            self.layer = self.text_layer
            self.delay(name='clear_delay', event_type=None, delay=time, handler=self.clear)

            #play sound
            self.game.sound.play('tilt_warining')

        def clear(self):
            self.layer = None

        def sw_plumbBobTilt_active(self, sw):
            if self.times_warned == self.game.user_settings['Standard']['Tilt Warnings']:
		self.tilt()
            else:
                self.warning()
			