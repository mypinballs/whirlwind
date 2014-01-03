# Switched Coils Control Mode - System 11
# myPinballs Feb 2013


import procgame
import locale
import logging
from procgame import *


base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"

class SwitchedCoils(game.Mode):

	def __init__(self, game, priority):
            super(SwitchedCoils, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.switched_coils')

            self.a_coils =['outhole','shooterLaneFeeder','rampLifter','leftLockKickback','topEject','knocker','dropTargetReset','singleDropTargetReset']
            self.c_coils = ['bottomRightFlasher','spinnerFlasher','rampTopFlasher','rampUMFlasher','rampLMFlasher','rampBottomFlasher','dropTargetFlasher','compassFlasher']

            self.switched_flag = False


        def mode_started(self):
            pass

        
        def drive(self,name,style='medium',cycle=0,time=2):
            for i in range(len(self.a_coils)):
                if name==self.a_coils[i]:
                    #experimental a side - allow for switching of relay and restore (for flashers that are previously scheduled)
                    self.game.coils.acSelect.disable()
                    wait=0.05 #50ms
                    self.delay(delay=wait,handler=self.game.coils[self.a_coils[i]].pulse)
                    wait+=self.game.coils[self.a_coils[i]].default_pulse_time
                    self.delay(delay=wait,handler=self.game.coils.acSelect.enable)

                    self.log.debug('Switched Coil Pulsed:%s',name)

                elif name==self.c_coils[i]:
                    self.game.coils.acSelect.enable()
                    if self.game.ac_relay.is_working():
                        self.switch_tries=0
                        data = [self.a_coils[i],style,cycle,time]
                        self.flasher(data)

                    self.log.debug('Flasher Scheduled:%s',name)

        #flasher control - check that ac relay is switched before starting effect
        #try 10 times before giving up  - TODO - inform ac relay mode that relay is bust in this case
        def flasher(self,data):
             self.log.debug('Switch flag:%s',self.switched_flag)
             if self.switched_flag:
                 self.game.effects.drive_flasher(data[0],data[1],data[2],data[3])
                 self.switch_tries=0
             elif self.switch_tries<10:
                 self.delay(name='cside_retry',delay=0.1,handler=self.flasher,param=data)
                 self.switch_tries+=1

        #disable the drive
        def disable(self,name):
            for i in range(len(self.a_coils)):
                if name==self.a_coils[i] or name==self.c_coils[i]:
                    self.game.coils[self.a_coils[i]].disable()


        #switch handlers
        def sw_csidePower_active(self, sw):
            self.switched_flag=True

        def sw_csidePower_inactive(self, sw):
            self.switched_flag=False