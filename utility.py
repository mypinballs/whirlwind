# Top Rollover Lanes

__author__="jim"
__date__ ="$Jan 18, 2011 1:36:37 PM$"


import procgame
import locale
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/indyjones/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"

class Utility(game.Mode):

	def __init__(self, game):
            super(Utility, self).__init__(game, 90)

            self.game.sound.register_sound('elephant_alert', sound_path+"elephant.aiff")

        def ball_missing(self):
            text_layer = dmd.TextLayer(128/2, 7, self.game.fonts['num_09Bx7'], "center", opaque=False)

            multiple = ''
            balls_missing = self.game.num_balls_total - self.game.num_balls()
            if balls_missing>1:
                multiple='s'
            text_layer.set_text(str(balls_missing)+" BALL"+multiple+" MISSING",1.5,5)#on for 1.5 seconds 5 blinks
            self.layer = text_layer
            self.game.sound.play('elephant_alert')

        
def boolean_format(value):
        if value=='Yes':
            return True
        else:
            return False
