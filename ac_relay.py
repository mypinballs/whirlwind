# AC Relay Code - System 11
# myPinballs September 2013

import procgame
import locale
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"

class ACRelay(game.Mode):

	def __init__(self, game, priority):
            super(ACRelay, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.ac_relay')

            self.working_flag = False




        def mode_started(self):
            self.initialise()


        def initialise(self):
            self.log.info("Testing AC Relay")
            self.repeats = 0
            self.test()


        def test(self):
            self.game.coils.acSelect.pulse(200)
            if self.repeats<5:
                self.delay(name='ac_relay_test_repeat',delay=0.5,handler=self.test)
                self.repeats+=1
            else:
                self.cancel_delayed('ac_relay_test_repeat')
                self.finish()

        def finish(self):
            if self.working_flag:
                self.log.info('AC relay is working')

            else:
                self.log.info('AC relay is broken. Check power and interconnect board')


        def is_working(self):

            return self.working_flag


        def sw_csidePower_active(self, sw):
            self.working_flag = True


