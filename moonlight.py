#Moonlight Madness Mode

import procgame
import locale
import random
import logging
import audits
from procgame import *
from drops import *
from tornado import *
from cellar import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class Moonlight(game.Mode):

	def __init__(self, game, priority):
            super(Moonlight, self).__init__(game, priority)

            self.log = logging.getLogger('whirlwind.moonlight_madness')

            self.game.sound.register_music('lock_lit', music_path+"lock_lit.ogg")
            self.game.sound.register_music('multiball_play', music_path+"multiball_play.ogg")
            self.game.sound.register_music('multiball_end', music_path+"multiball_end.aiff")

            self.game.sound.register_sound('take_cover_now', speech_path+"take_cover_now.ogg")
            self.game.sound.register_sound('multiball_eject_speech', speech_path+"here_it_comes.ogg")
            self.game.sound.register_sound('million_speech', speech_path+"ooh_million.ogg")
            self.game.sound.register_sound('whirlwind_speech', speech_path+"whirlwind.ogg")

            self.game.sound.register_sound('random_sound1', sound_path+"pop_1.ogg")
            self.game.sound.register_sound('random_sound2', sound_path+"pop_2.ogg")
            self.game.sound.register_sound('random_sound3', sound_path+"pop_3.ogg")
            self.game.sound.register_sound('random_sound4', sound_path+"pop_4.ogg")
            self.game.sound.register_sound('random_sound5', sound_path+"pop_5.ogg")
            self.game.sound.register_sound('random_sound6', sound_path+"drop_target_hit.ogg")
            self.game.sound.register_sound('random_sound7', sound_path+"drop_target_sweep.ogg")
            self.game.sound.register_sound('random_sound8', sound_path+"inlane_1.ogg")
            self.game.sound.register_sound('random_sound9', sound_path+"inlane_2.ogg")
            self.game.sound.register_sound('random_sound10', sound_path+"compass_target_lit.ogg")
            self.game.sound.register_sound('random_sound11', sound_path+"cow_3.aiff")
            self.game.sound.register_sound('random_sound12', sound_path+"glass_smash.aiff")

            self.game.sound.register_sound('saucer_eject', sound_path+"saucer_eject.aiff")


            self.flashers = ['rampBottomFlasher','rampLMFlasher','rampUMFlasher','rampTopFlasher','spinnerFlasher','bottomRightFlasher']
            self.lightning_flashers = ['lightningLeftFlasher','lightningMiddleFlasher','lightningRightFlasher']

            self.enter_value = 10
            self.made_value_base = 50000
            self.made_value_boost = 10000
            self.made_value_max = 100000
            self.skyway_toll_boost = 3
            self.super_combo_multiplier = 10
            self.combo_multiplier = 2
            self.million_value = 1000000
            self.million_timer = 30 #change to setting
            self.base_value = 250000

            self.balls_needed = 3
            self.next_ball_ready = False
            self.virtual_lock = False
            self.multiball_info_text_flag = 0
            self.end_callback= None
            

            self.moonlight_switchnames = []
            for switch in self.game.switches.items_tagged('moonlight'):
                self.moonlight_switchnames.append(switch.name)

            # Install switch handlers.
            for switch in self.moonlight_switchnames:
		self.add_switch_handler(name=switch, event_type='active',delay=None, handler=self.progress)


        
        def reset(self):
            self.count = 0
            self.million_count = 0
            self.total = 0
            self.played_flag = False
            self.start_finish = False
            self.ball_ejected = False

            self.reset_display_flag()
            self.reset_combos()
            

        def reset_combos(self):
            self.combo = False
            self.super_combo = False

        def reset_display_flag(self):
            self.progress_text_runnning = False


#        def update_lamps(self):
#            for i in range(self.lamps):
#                self.game.effects.drive_lamp(self.lamps[i],'on')
#

        def multiball_lamps(self, enable=True):
            # Start the lamps doing a crazy rotating sequence:
            schedules = [0xffff000f, 0xfff000ff, 0xff000fff, 0xf000ffff, 0x000fffff, 0x00fffff0, 0x0fffff00, 0xfffff000]
            for index, lamp in enumerate(sorted(self.game.lamps, key=lambda lamp: lamp.number)):
                if enable:
                    sched = schedules[index%len(schedules)]
                    lamp.schedule(schedule=sched, cycle_seconds=0, now=False)
                else:
                    lamp.disable()


        def mode_started(self):
            self.multiball_ready = self.game.get_player_stats('multiball_ready')
            self.multiball_started = self.game.get_player_stats('multiball_started')
            self.multiball_running = self.game.get_player_stats('multiball_running')
            self.million_lit = self.game.get_player_stats('million_lit')

            #setup
            self.game.enable_flippers(True)
            self.game.tilt.reset()
            self.game.ball_search.enable()

            #set gi
            self.game.coils.upperPlayfieldGIOff.enable()
            self.game.coils.lowerPlayfieldGIOff.disable()

            self.multiball_start()

            self.reset()

            #add other modes to utilise mechanisms and other logic
            self.drops = Drops(self.game,41)
            self.tornado = Tornado(self.game,41)
            self.cellar = Cellar(self.game,43)

            self.game.modes.add(self.drops)
            self.game.modes.add(self.tornado)
            self.game.modes.add(self.cellar)


            
        def mode_stopped(self):
            #tidy up
            self.multiball_ready = False
            self.game.set_player_stats('multiball_ready',self.multiball_ready)

            #set the played flag to true so only happens once per player if enabled
            self.played_flag = True
            self.game.set_player_stats('moonlight_status',self.played_flag)
            #store the total value for the round
            self.game.set_player_stats('moonlight_total',self.total)

            #remove other modes
            self.game.modes.remove(self.drops)
            self.game.modes.remove(self.tornado)
            self.game.modes.remove(self.cellar)

            #continue game
            self.game.ball_starting()


        def mode_tick(self):
            if self.multiball_started:
                self.balls_in_play = self.game.trough.num_balls_in_play

                #debug
                #self.balls_in_play=3
                #-------------------------------------------
                #debug_ball_data = str(self.balls_in_play)+":"+str(self.game.trough.num_balls())+":"+str(self.game.trough.num_balls_locked)+":"+str(self.game.trough.num_balls_to_launch)+":"+str(self.multiball_running)
                #self.game.set_status(debug_ball_data)
                #self.game.score_display.set_text(debug_ball_data.upper(),1,'left')
                #self.log.debug(debug_ball_data)
                #-------------------------------------------

                if self.balls_in_play==self.balls_needed and self.multiball_running==False:
                    #start tracking
                    self.multiball_running = True;
                    self.game.set_player_stats('multiball_running',self.multiball_running)


                if self.multiball_running:
                    self.cancel_delayed('display_multiball_info_repeat')
                    self.multiball_tracking()



        def million_speech(self,enable=True):
            if enable:
                self.game.sound.play_voice('million_speech')
                self.delay('million_speech_repeat',delay=60,handler=self.million_speech)
            else:
                self.cancel_delayed('million_speech_repeat')


        def spin_wheels(self):
            num=random.randint(50,150)
            self.game.coils.spinWheelsMotor.pulse(num)
            self.delay(name='spin_wheels_repeat',delay=0.8,handler=self.spin_wheels)



        def display(self, top, bottom, seconds, opaque=True, repeat=False, hold=False, frame_time=3):
            self.game.score_display.set_transition_reveal(text=top.upper(),row=0,seconds=seconds)
            self.game.score_display.set_transition_reveal(text=bottom.upper(),row=1,seconds=seconds)

        
     
        def display_million_text(self,time=2):
            self.display(top='1 Million',bottom='Million',seconds=time)


        def display_multiball_info(self,time=3):
            if self.multiball_info_text_flag%2==0:
                self.display(top='Moonlight',bottom='Madness',seconds=time)
            else:
                self.display(top='All Switches',bottom=locale.format("%d", self.base_value, True),seconds=time)

            if self.multiball_info_text_flag<10:
                self.multiball_info_text_flag+=1
                self.cancel_delayed('display_multiball_info_repeat')
                self.delay(name='display_multiball_info_repeat',delay=time+1,handler=self.display_multiball_info,param=time)
            else:
                self.multiball_info_text_flag = 0
                self.cancel_delayed('display_multiball_info_repeat')

            
        def display_progress_text(self,time=3):
            text=['***Pow***','***Wham***','***Kepow***','***Doho***','***Cow***','***Slam***','***Crash***','***Boom***','***Bang***','***Kezamm***']
            num = random.randint(0,len(text)-1)
            self.display(top=text[num],bottom=text[num],seconds=time)
            self.progress_text_runnning = True
            self.delay(name='clear_progress_display_flag_timer',delay=time+1,handler=self.reset_display_flag)


        def display_total_text(self,time=0):
             self.display(top='Moonlight Total',bottom=locale.format("%d", self.total, True),seconds=time)

        def display_finish_text(self,time=0):
             self.display(top='And Now',bottom='Back To The Game',seconds=time)


        def strobe_flashers(self,time=0.1):
            timer = 0
            repeats = 4

            #lightning flashers
            self.game.effects.strobe_flasher_set(self.lightning_flashers,time=time,overlap=0.2,repeats=repeats)

            #playfield flashers
            sequence=[]
            for j in range(repeats):
                sequence += self.flashers

            for i in range(len(sequence)):

                def flash(i,time,delay):
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='fast',time=time+0.1))

                flash(i,time,timer)
                timer+=time

        def progress_flashers(self,time=0.1):
            timer = 0
            sequence = []

            #playfield flashers
            flashers = self.flashers
            sequence+=flashers
            flashers.reverse()
            sequence+flashers

            for i in range(len(sequence)):

                def flash(i,time,delay):
                    self.delay(delay=delay,handler=lambda:self.game.switched_coils.drive(name=sequence[i],style='fast',time=time+0.1))

                flash(i,time,timer)
                timer+=time


        def play_sound(self):

            list =["random_sound1","random_sound2","random_sound3","random_sound4","random_sound5","random_sound6","random_sound7","random_sound8","random_sound9","random_sound10","random_sound11","random_sound12"]
            i= random.randint(0, len(list)-1)
            self.game.sound.play(list[i])


        def multiball_start(self):
            self.log.debug('multiball start reached')

            #update the flag
            self.multiball_started = True
            self.game.set_player_stats('multiball_started',self.multiball_started)

            #display help info
            self.display_multiball_info(3)

            #ramp down
            self.game.coils['rampDown'].pulse()

            #play speech
            start_speech_length = self.game.sound.play_voice('multiball_eject_speech')

            #change music
            self.game.sound.stop_music()
            self.game.sound.play_music('multiball_play',-1)

            self.delay(name='multiball_eject_delay',delay=start_speech_length+0.5, handler=self.multiball_eject)

            audits.record_value(self.game,'moonlightMultiballStarted')


        def multiball_eject(self):
            self.log.debug('multiball eject reached')

            #make sure ramp is up
            self.skyway_entrance('up')

            #launch balls
            self.game.trough.launch_balls(3,stealth=False) #launch balls

            #queue multiball effects
            self.delay(name='multiball_effects_delay',delay=0.5, handler=self.multiball_effects)


        def multiball_effects(self):
            #jackpot lit
            self.lite_million()

            #spin wheels
            self.spin_wheels()

            #run flasher effects
            self.strobe_flashers()

            #start lamp effects
            self.multiball_lamps()

            #turn on ball save
            self.game.ball_save.start(num_balls_to_save=5,allow_multiple_saves=True,time=20)


        def multiball_tracking(self):
            #end check
            if self.balls_in_play==1 and not self.start_finish:

                #update flag
                self.start_finish = True

                #stop spinning wheels
                self.cancel_delayed('spin_wheels_repeat')

                #cancel award
                self.lite_million(False)

                #disable all lamps
                for lamp in self.game.lamps:
                    lamp.disable()

                #stop music
                self.game.sound.stop_music()
                self.game.sound.play_music('multiball_end',loops=0)

                #multiball ended callback
                if self.end_callback:
                    self.log.debug('Moonlight Multiball End Callback Called')
                    self.end_callback()

                #disable flippers
                self.game.enable_flippers(enable=False)

                #calc total & display
                self.total = (self.count*self.base_value)+(self.million_count*self.million_value)
                self.display_total_text()


            elif self.balls_in_play==0: #all balls now drained

                #end tracking & update player stats
                self.multiball_running=False
                self.multiball_started = False
                self.multiball_ready = False

                self.game.set_player_stats('multiball_running',self.multiball_running)
                self.game.set_player_stats('multiball_started',self.multiball_started)
                self.game.set_player_stats('multiball_ready',self.multiball_ready)
                
                #zero score
                self.game.current_player().score = 0

                wait =3
                self.display_finish_text(wait)
                self.delay(delay=wait,handler=self.finish)     
    

        def finish(self):
            self.game.modes.remove(self)


        def spin_wheels(self):
            range=[]
            delay=0
            if self.multiball_started:
                range=[50,200]
                delay=0.7
            else:
                range=[50,150]
                delay=0.8

            num=random.randint(range[0],range[1])
            self.game.coils.spinWheelsMotor.pulse(num)
            self.delay(name='spin_wheels_repeat',delay=0.7,handler=self.spin_wheels)


        def lite_million(self,enable=True):
            if enable:
                self.million_lit=True
                self.log.debug('Million is Lit')

                self.game.switched_coils.drive(name='rampUMFlasher',style='fast')#schedule million flasher for unlimited time
                self.game.effects.drive_lamp('million','fast')

            else:
                self.game.switched_coils.drive(name='rampUMFlasher',style='off')
                self.game.effects.drive_lamp('million','off')
                self.million_lit=False

            self.million_speech(enable)
            self.game.set_player_stats('million_lit',self.million_lit)
           


        def award_million(self):
            self.cancel_delayed('million_timer')
            self.cancel_delayed('million_speech')
            
            self.display_million_text()
            self.game.score(self.million_value)
            #self.game.sound.play_voice('whirlwind_speech')
            self.delay(name='award_speech_delay',delay=1,handler=lambda:self.game.sound.play_voice('whirlwind_speech'))
            self.game.switched_coils.drive(name='rampUMFlasher',style='fast',time=1)

            #reset
            #self.lite_million(False)

            #inc the count
            self.million_count+=1

            #update audits
            audits.record_value(self.game,'millionCollected')


        def skyway_entrance(self,dirn):
            if dirn=='up' and self.game.switches.rightRampDown.is_active():
                self.game.switched_coils.drive('rampLifter')
            elif dirn=='down' and self.game.switches.rightRampDown.is_inactive():
                self.game.coils['rampDown'].pulse()


        def saucer_eject(self):
            self.game.sound.play('saucer_eject')
            self.game.switched_coils.drive('topEject')
            if not self.ball_ejected:
                self.delay(name='saucer_eject_repeat',delay=1.5,handler=self.saucer_eject)


        def progress(self,sw):
            if self.multiball_running and not self.start_finish:
                if not self.progress_text_runnning:
                    self.display_progress_text()
                self.game.score(self.base_value)
                self.progress_flashers()
                self.play_sound()

                if self.count%10==0:
                    self.game.effects.strobe_flasher_set(self.lightning_flashers,time=0.1,overlap=0.2,repeats=2)

                self.count+=1



        #switch handlers
        #-------------------------

        def sw_leftRampMadeTop_active(self, sw):
            if self.multiball_running:
                self.award_million()


        def sw_topRightEject_active_for_200ms(self, sw):
            if self.multiball_running:
                self.ball_ejected = False
                self.saucer_eject()


        def sw_topRightEject_inactive_for_200ms(self, sw):
            self.ball_ejected =True
            self.cancel_delayed('saucer_eject_repeat')

                
#        def sw_shooterLane_open_for_1s(self,sw):
#            if not self.multiball_running:
#                self.multiball_start()


        def sw_shooterLane_active_for_500ms(self,sw):
            if self.multiball_started and not self.multiball_running and self.game.auto_launch_enabled:
                self.game.coils.autoLaunch.pulse()

