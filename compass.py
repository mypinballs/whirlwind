#Compass Mode

import procgame
import locale
import random
import logging
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Compass(game.Mode):

	def __init__(self, game, priority, mode1=None, mode2=None):
            super(Compass, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.compass')
            self.multiball = mode1
            self.auxmode2 = mode2

            #self.hits_layer = dmd.TextLayer(100, 0, self.game.fonts['num_14x10'], "center", opaque=False)
            self.game.sound.register_music('lock_lit', music_path+"lock_lit.ogg")
            self.game.sound.register_music('end', music_path+"lock_lit_end.ogg")

            self.game.sound.register_sound('target_lit', sound_path+"compass_target_lit.ogg")
            self.game.sound.register_sound('target_unlit', sound_path+"thunder_crack.ogg")
            
            self.game.sound.register_sound('storm_coming_long', speech_path+"storm_coming_return.ogg")
            self.game.sound.register_sound('storm_coming', speech_path+"storm_coming.ogg")
            self.game.sound.register_sound('storm_over', speech_path+"storm_over_all_clear.ogg")


            self.nwlamps=['nwTop','nwBottom']
            self.nelamps =['neTop','neBottom']
            self.swlamps=['swTop','swBottom']
            self.selamps=['seTop','seBottom']

            self.lamps=self.nwlamps+self.nelamps+self.swlamps+self.selamps

            self.directions=['nw','ne','sw','se']
            self.base_directions=['n','e','s','w']

            self.target_unlit_value = 40000
            self.target_lit_value = 25000
            self.ball_locked_value = 50000

            self.set1=[]
            self.set2=[]
            self.balls_needed =3

            self.next_ball_ready = False


        def reset(self):
            self.shots_made = 0
            self.set_complete = 0
            self.game.coils.divertor.disable()

            for i in range(len(self.flags)):#reset flags
                self.flags[i]=0

            self.set_chase()


        def reset_lamps(self):
            for i in range(len(self.lamps)):
                 self.game.effects.drive_lamp(self.lamps[i],'off')


        def update_lamps(self):
            self.log.info("updating compass lamps")
            for i in range(len(self.directions)):
                flag_sum=0
                for j in range(2):
                    
                    self.log.debug("compass flag%s:%s",(2*i)+j,self.flags[(2*i)+j])
                    #update the target lamps
                    if self.flags[(2*i)+j]==1:
                        self.game.effects.drive_lamp(self.lamps[(2*i)+j],'medium')
                        flag_sum+=1
                    elif self.flags[(2*i)+j]==2:
                        self.game.effects.drive_lamp(self.lamps[(2*i)+j],'on')
                        flag_sum+=2
                    else:
                        self.game.effects.drive_lamp(self.lamps[(2*i)+j],'off')

                #update the compass lamps
                self.log.debug('flagsum:%s',flag_sum)
                if flag_sum>=2 and flag_sum<4:
                    self.game.effects.drive_lamp(self.directions[i]+'Compass','medium')
                elif flag_sum==4:
                    self.game.effects.drive_lamp(self.directions[i]+'Compass','on')
                else:
                    self.game.effects.drive_lamp(self.directions[i]+'Compass','off')


        def set_lamps(self,num):
            self.game.effects.drive_lamp(self.lamps[num],'smarton')

        def completed_lamps(self,timer):
            #effect could do strobing around compass here
            for i in range(len(self.directions)):
                flag_sum=0
                for j in range(2):
                    if self.flags[(2*i)+j]==2:
                        self.game.effects.drive_lamp(self.lamps[(2*i)+j],'superfast')

            self.delay(delay=timer,handler=self.update_lamps)
            
        def mode_started(self):

            self.compass_level = self.game.get_player_stats('compass_level')
            self.set_complete = self.game.get_player_stats('compass_sets_complete')
            self.flags= self.game.get_player_stats('compass_flags')
            self.million_lit = self.game.get_player_stats('million_lit')

            self.lock_lit = self.game.get_player_stats('lock_lit')
            self.balls_locked =  self.game.get_player_stats('balls_locked')
            self.multiball_started = False
            self.multiball_ready = self.game.get_player_stats('multiball_ready')

            #setup the compass
            self.reset()

            
        def mode_stopped(self):
            self.game.set_player_stats('compass_level',self.compass_level)
            self.game.set_player_stats('compass_flags',self.flags)
            self.game.set_player_stats('compass_sets_complete',self.set_complete)
            self.game.set_player_stats('lock_lit',self.lock_lit)
            self.game.set_player_stats('multiball_ready',self.multiball_ready)

            
        def set_chase(self):
            if self.compass_level==1:
                self.set1=['nw','ne']
            elif self.compass_level==2:
                self.set1=['nw','se']
            elif self.compass_level==3:
                self.set1=['nw','ne']
                self.set2=['nw','se']
            elif self.compass_level==4:
                self.set1=['se','sw']
                self.set2=['nw','ne']

            for i in range(len(self.flags)):#reset flags
                self.flags[i]=0

            for i in range(len(self.directions)):
                
                if self.set_complete==0: #setup the first set
                    for j in range(len(self.set1)):
                        if self.directions[i]==self.set1[j]:
                            for k in range(2):
                                self.flags[(i*2)+k]=1

                elif self.set_complete==1:  #setup the second set
                    for j in range(len(self.set2)):
                        if self.directions[i]==self.set2[j]:
                            for k in range(2):
                                self.flags[(i*2)+k]=1

            self.update_lamps()
                        
        def lock_ready(self):
            self.lock_lit=True
            self.game.set_player_stats('lock_lit',self.lock_lit)

            self.display_status_text(top='lock lit',bottom='',seconds=2)

            self.game.sound.stop_music()
            self.game.sound.play_music('lock_lit',-1)
            self.delay(name='lock_lit_announce',delay=1,handler=lambda:self.game.sound.play_voice('storm_coming_long'))

            self.game.effects.drive_lamp('lock','smarton')
            
            
        def ball_locked(self):
           
            self.display_status_text(top='ball '+str(self.balls_locked)+' locked',bottom='',seconds=2)

            if self.balls_locked<2:
                self.game.sound.stop_music()
                self.game.sound.play_music('general_play',-1)
                self.delay(name='ball_locked_announce',delay=1,handler=lambda:self.game.sound.play_voice('storm_over'))

                self.lock_lit=False
                self.game.set_player_stats('lock_lit',self.lock_lit)
                self.game.effects.drive_lamp('lock','off')
            else:
                self.game.switched_coils.drive('rightRampLifter')
                self.delay(name='ball_locked_announce',delay=1,handler=lambda:self.game.sound.play_voice('storm_coming'))
                self.game.effects.drive_lamp('release','smarton')


        def launch_next_ball(self):
            self.game.trough.launch_balls(1,stealth=False) #stealth false, bip +1
            self.next_ball_ready = True
            self.game.ball_save.start(time=5)
            

        def display_text(self, count, value, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_text(str(count)+' skyway tolls'.upper(),0,'center',seconds=2)
            self.game.score_display.set_text('+'+locale.format("%d", value, True),1,'center',seconds=2)


        def display_status_text(self, top, bottom, seconds, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_text(top.upper(),0,'center',seconds=seconds)
            self.game.score_display.set_text(bottom.upper(),1,'center',seconds=seconds)

        
        def score(self,value):
            self.game.score(value)

        def get_direction_index(self,direction):
            for x in range(len(self.directions)):
                if direction==self.directions[x]:
                    return x

        def check_chase_progress(self):
            if self.set_complete ==0:
                count=0
                for i in range(len(self.set1)):
                    num=self.get_direction_index(self.set1[i])
                    if self.flags[num*2]==2 and self.flags[(num*2)+1]==2:
                        self.game.effects.drive_lamp(self.directions[num]+'Compass','smarton')
                        count+=1

                if count==len(self.set1):
                    if len(self.set2)>0: #determine if there is a second set in sequence
                        self.set_complete=1
                        self.completed_lamps(1)
                        self.delay(delay=1,handler =self.set_chase)
                    else:
                        self.set_complete=2
                        self.completed_lamps(1)
                        self.lock_ready()

            elif self.set_complete==1:

                count=0
                for i in range(len(self.set2)):
                    num=self.get_direction_index(self.set2[i])
                    if self.flags[num*2]==2 and self.flags[(num*2)+1]==2:
                        self.game.effects.drive_lamp(self.directions[num]+'Compass','smarton')
                        count+=1

                if count==len(self.set2):
                    self.set_complete=2
                    self.completed_lamps(1)
                    self.lock_ready()


        def progress(self,num):
            if self.flags[num]==1:
                self.flags[num]=2
                self.log.debug('Compasss Flags Status:%s',self.flags)

                self.set_lamps(num)
                self.game.sound.play('target_unlit')
                self.score(self.target_unlit_value)
                self.check_chase_progress()
                self.update_lamps()
            else:
                self.game.sound.play('target_lit')
                self.score(self.target_lit_value)

            

        def lock_manager(self):
            self.balls_locked+=1
            self.game.set_player_stats('balls_locked', self.balls_locked)

            #update trough
            self.game.trough.num_balls_locked = self.balls_locked
            self.game.trough.num_balls_in_play -=1

            if self.balls_locked==self.balls_needed:
                #set flag
                self.multiball.multiball_started = True
                self.multiball.multiball_start()

                self.lock_lit=False
                self.game.set_player_stats('lock_lit',self.lock_lit)
                self.game.effects.drive_lamp('lock','off')
                self.game.effects.drive_lamp('release','off')
                self.game.coils.divertor.disable()

            else:
                self.ball_locked()
                self.launch_next_ball()
                self.compass_level+=1
                self.reset()



        #switch handlers

        def sw_leftStandup_active(self, sw):
            #nw2
            self.progress(1)

        def sw_leftInlane_active(self, sw):
            #ne2
            self.progress(3)

        def sw_leftLoopBottom_active(self, sw):
            #sw2
            self.progress(5)

        def sw_rightStandup_active(self, sw):
            #se2
            self.progress(7)

        def sw_leftStandupRightRamp_active(self, sw):
            #nw1
            self.progress(0)

        def sw_rightStandupRightRamp_active(self, sw):
            #ne1
            self.progress(2)

        def sw_innerLoop_active(self, sw):
            #sw1
            self.progress(4)

        def sw_rightLoopBottom_active(self, sw):
            #se1
            self.progress(6)


        def sw_rightRampMadeTop_active(self, sw):
            if self.lock_lit:
                self.game.coils.divertor.patter(original_on_time=30, on_time=2, off_time=18)


        #lock lane switches
        def sw_lock1_active_for_500ms(self, sw):
            if self.balls_locked==0:
                self.lock_manager()

        def sw_lock2_active_for_500ms(self, sw):
            if self.balls_locked==1:
                self.lock_manager()

        def sw_lock3_active_for_500ms(self, sw):
            if self.balls_locked==2:
                self.lock_manager()


        #start ball save for next ball after lock
        def sw_shooterLane_open_for_1s(self,sw):
            if self.next_ball_ready:

            	ball_save_time = 5
                self.game.ball_save.start(num_balls_to_save=1, time=ball_save_time, now=True, allow_multiple_saves=False)
                self.next_ball_ready = False

        #start multiball via eject
        def sw_topRightEject_active_for_250ms(self, sw):
            if self.balls_locked==2 & self.lock_lit:
                self.lock_manager()
                self.delay(name='release_ball',delay=2,handler=lambda:self.game.switched_coils.drive('topEject'))

            else:
                self.game.switched_coils.drive('topEject')

        #start multiball via ramp
        def sw_leftRampMadeTop_active(self, sw):
            if self.balls_locked==2 & self.lock_lit:
                self.lock_manager()