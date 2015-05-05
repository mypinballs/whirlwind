import logging
import locale
import audits
from procgame import *

base_path = config.value_for_key_path('base_path')
game_path = base_path+"games/whirlwind/"
speech_path = game_path +"speech/"
sound_path = game_path +"sound/"
music_path = game_path +"music/"

class ServiceModeSkeleton(game.Mode):
	"""Service Mode List base class."""
	def __init__(self, game, priority, font):
		super(ServiceModeSkeleton, self).__init__(game, priority)
                self.log = logging.getLogger('whirlwind.service')
		self.name = ""
#                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
#		self.title_layer = dmd.TextLayer(1, 0, font, "left")
#		self.item_layer = dmd.TextLayer(1, 11, self.game.fonts['8x6'], "left")
#		self.instruction_layer = dmd.TextLayer(1, 25, font, "left")
#                self.instruction_layer.composite_op = "blacksrc"
#		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.instruction_layer])
#		self.no_exit_switch = game.machine_type == 'sternWhitestar'

	def mode_started(self):
		#self.title_layer.set_text(str(self.name))
                self.game.score_display.cancel_script()
                self.game.score_display.set_text(text=str(self.name).upper(),row=0,justify='left',opaque=True)
		self.game.sound.play('service_enter')

	def mode_stopped(self):
		self.game.sound.play('service_exit')
                self.game.score_display.reset()
               

	def disable(self):
		pass

#	def sw_down_active(self, sw):
#		if self.game.switches.enter.is_active():
#			self.game.modes.remove(self)
#			return True

#	def sw_exit_active(self, sw):
#		self.game.modes.remove(self)
#		return True

        def sw_enter_active(self,sw):
            if self.game.switches.direction.is_inactive():
                self.game.modes.remove(self)
		return True


class ServiceModeList(ServiceModeSkeleton):
	"""Service Mode List base class."""
	def __init__(self, game, priority, font):
		super(ServiceModeList, self).__init__(game, priority, font)
		self.items = []

	def mode_started(self):
		super(ServiceModeList, self).mode_started()
                self.game.score_display.cancel_script()
		self.iterator = 0
		self.change_item()

	def change_item(self):
		ctr = 0
                for item in self.items:
			if (ctr == self.iterator):
				self.item = item
			ctr += 1
		self.max = ctr - 1
		#self.item_layer.set_text(self.item.name)
                self.game.score_display.set_text(text=str(self.item.name[:16]).upper(),row=0,justify='left',opaque=True)

	def sw_step_active(self,sw):
		if self.game.switches.direction.is_active():
			self.item.disable()
			if (self.iterator < self.max):
				self.iterator += 1
                        else:
                            self.iterator =0
			self.game.sound.play('service_next')
			self.change_item()
                elif self.game.switches.direction.is_inactive():
			self.item.disable()
			if (self.iterator > 0):
				self.iterator -= 1
                        else:
                            self.iterator =self.max
			self.game.sound.play('service_previous')
			self.change_item()
		
		return True

	def sw_enter_active(self,sw):
                if self.game.switches.direction.is_active():
                    self.game.modes.add(self.item)
                    return True
                elif self.game.switches.direction.is_inactive():
                    self.exit()
                    
                    
	def exit(self):
		self.item.disable()
		self.game.modes.remove(self)
		return True


class ServiceMode(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font,big_font, extra_tests=[]):
		super(ServiceMode, self).__init__(game, priority,font)
		#self.title_layer.set_text('Service Mode')
                
                #setup sounds
                self.game.sound.register_sound('service_enter', sound_path+"menu_in.wav")
		self.game.sound.register_sound('service_exit', sound_path+"menu_out.wav")
		self.game.sound.register_sound('service_next', sound_path+"next_item.wav")
		self.game.sound.register_sound('service_previous', sound_path+"previous_item.wav")
		self.game.sound.register_sound('service_switch_edge', sound_path+"switch_edge.wav")
		self.game.sound.register_sound('service_save', sound_path+"save.wav")
		self.game.sound.register_sound('service_cancel', sound_path+"cancel.wav")
                self.game.sound.register_sound('service_alert', sound_path+"service_alert.aiff")
                
		self.name = 'Service Mode'
		self.tests = Tests(self.game, self.priority+1, font, big_font, extra_tests)
		self.items = [self.tests]
		if len(self.game.settings) > 0: 
			self.settings = Settings(self.game, self.priority+1, font, big_font, 'Settings', self.game.settings)
			self.items.append(self.settings)


		if len(self.game.game_data) > 0: 
			self.statistics = Statistics(self.game, self.priority+1, font, big_font, 'Statistics', self.game.game_data)
			self.items.append(self.statistics)
                        
        def mode_stopped(self):
            super(ServiceMode, self).mode_stopped()
            self.game.coin_door.load_messages()


class Tests(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, extra_tests=[]):
		super(Tests, self).__init__(game, priority,font)
		#self.title_layer.set_text('Tests')
		self.name = 'Tests'
		self.lamp_test = LampTest(self.game, self.priority+1, font, big_font)
		self.coil_test = CoilTest(self.game, self.priority+1, font, big_font)
		self.switch_test = SwitchTest(self.game, self.priority+1, font, big_font)
		self.items = [self.switch_test, self.lamp_test, self.coil_test]
		for test in extra_tests:
			self.items.append(test)

class LampTest(ServiceModeList):
	"""Lamp Test"""
	def __init__(self, game, priority, font, big_font):
		super(LampTest, self).__init__(game, priority,font)
                #set mode name
		self.name = "Lamp Test"

                #set layers
#                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/switch_test_bgnd.dmd').frames[0])
#		self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
#                self.matrix_layer.composite_op = "blacksrc"
#                self.matrix_layer.target_x = 128
#                self.matrix_layer.target_y = 32
#                self.title_layer = dmd.TextLayer(1, 0, font, "left")
#                self.instruction_layer = dmd.TextLayer(45, 0, font, "left")
#		self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
#                self.board_layer = dmd.TextLayer(1, 18, font, "left")
#                self.drive_layer = dmd.TextLayer(1, 24, font, "left")
#                self.row_layer = dmd.TextLayer(1, 18, font, "left")
#                self.column_layer = dmd.TextLayer(1, 24, font, "left")
#                self.number_layer = dmd.TextLayer(99, 24, font, "right")
#		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.instruction_layer,self.item_layer, self.row_layer,self.column_layer,self.number_layer,self.matrix_layer])

                #connector setup
                self.base_colour =['Red','Yellow']
                self.connector_key = [3,2]

                #populate connector colours
                for j in range (len(self.base_colour)):
                    self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White']
                    colour_set = self.colours
                    colour_set.pop(self.connector_key[j]-1)
                    for i in range(len(colour_set)):
                        if colour_set[i]==self.base_colour[j]:
                         colour_set[i] = "Black"
                    if j==0:
                        self.row_colour = colour_set
                    elif j==1:
                        self.col_colour = colour_set


		self.items = self.game.lamps

        def mode_started(self):
		super(LampTest, self).mode_started()
		self.action = 'repeat'
                #self.instruction_layer.set_text(' - Repeat')
                self.game.score_display.set_text(text=str(' - Repeat').upper(),row=0,justify='right',opaque=False)

                #self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_repeat)

        def mode_stopped(self):
                super(LampTest, self).mode_stopped()
                self.game.score_display.cancel_script()

	def change_item(self):
		super(LampTest, self).change_item()

                 #get the yaml numbering data for coils
                if self.item.yaml_number.count('L')>0:

                    matrix =[]
                    matrix.append(int(self.item.yaml_number[1])-1)
                    matrix.append(int(self.item.yaml_number[2])-1)
                    self.lamp_col = matrix[0]
                    self.lamp_row = matrix[1]

                self.game.score_display.cancel_script()
                
                script=[]
                #set text for the layers
                #self.item_layer.set_text(self.item.label)
                #script.append({'top':str(self.item.yaml_number+' '+self.item.label),'timer':3,'transition':3})
                
                #self.row_layer.set_text(self.base_colour[0]+' '+self.row_colour[self.lamp_row])
                script.append({'top':str(self.item.yaml_number+' '+self.item.label[:12]).upper(),'bottom':str('Row: '+self.base_colour[0]+'/'+self.row_colour[self.lamp_row]).upper(),'timer':3,'transition':2})
                #self.column_layer.set_text(self.base_colour[1]+' '+self.col_colour[self.lamp_col])
                script.append({'top':str(self.item.yaml_number+' '+self.item.label[:12]).upper(),'bottom':str('Col: '+self.base_colour[1]+'/'+self.col_colour[self.lamp_col]).upper(),'timer':3,'transition':2})
               
                #set the display text script
                self.game.score_display.set_script(script)
              
                #flash the lamp
		self.item.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=True)


	def sw_enter_active(self,sw):
                if self.game.switches.direction.is_active():
                    return True
                elif self.game.switches.direction.is_inactive():
                    self.item.disable()
                    self.game.modes.remove(self)
                    return True
		

class CoilTest(ServiceModeList):
	"""Coil Test"""
	def __init__(self, game, priority, font, big_font):
		super(CoilTest, self).__init__(game, priority, font)
		#set mode name
                self.name = "Coil Test"

                #setup layers
#                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/coil_test_bgnd.dmd').frames[0])
#		self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
#                self.matrix_layer.composite_op = "blacksrc"
#                self.matrix_layer.target_x = 128
#                self.matrix_layer.target_y = 32
#                self.title_layer = dmd.TextLayer(1, 0, font, "left")
#		self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
#                self.instruction_layer = dmd.TextLayer(45, 0, font, "left")
#                self.board_layer = dmd.TextLayer(1, 18, font, "left")
#                self.drive_layer = dmd.TextLayer(1, 24, font, "left")
#                self.conn_layer = dmd.TextLayer(100, 24, font, "right")
#		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.item_layer, self.board_layer,self.drive_layer,self.conn_layer,self.instruction_layer,self.matrix_layer])

                #setup mode lists
                self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White']
                self.bank_colours = ['Purple','Brown','Black','Blue']
                self.connector_key =[2,3,4,6]
                self.connections=['J120-13','J120-11','J120-9','J120-7','J120-6','J120-4','J120-3','J120-1','J116-1','J116-2','J116-4','J116-5','J116-6','J116-7','J117-3','J116-9','J113-1','J113-3']
                self.transistors=[90,92,87,89,84,86,81,83,72,68,71,67,70,66,69,65]

		self.items = self.game.coils
                    
		self.max = len(self.items)
                self.log.info("Max:"+str(self.max))

	def mode_started(self):
		super(CoilTest, self).mode_started()
		self.action = 'manual'
                #self.instruction_layer.set_text(' - Manual')
                self.game.score_display.set_text(text=str(' - Manual').upper(),row=0,justify='right',opaque=False)

                #check this line is needed
		if self.game.lamps.has_key('start'): self.game.lamps.start.schedule(schedule=0xff00ff00, cycle_seconds=0, now=False)

                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)


        def mode_stopped(self):
                super(CoilTest, self).mode_stopped()
                self.cancel_delayed('repeat')
                self.game.score_display.cancel_script()


        def change_item(self):
                self.log.info("items total:"+str(len(self.items)))
		ctr = 0
                for item in self.items:
                    if (ctr == self.iterator):
                        self.item = item

                    ctr += 1
                    self.log.info("item:"+str(item.label))
                
                coil_num =self.item.number-32+1
                
                self.game.score_display.cancel_script()
                script=[]
                if len(self.transistors)>coil_num:
                    script.append({'top':str(self.item.yaml_number+' '+self.item.label[:10]).upper(),'bottom':str("Q"+str(self.transistors[coil_num-1])+" Sol "+str(coil_num)).upper(),'timer':3,'transition':2})                  
                    script.append({'top':str(self.item.yaml_number+' '+self.item.label[:10]).upper(),'bottom':str(self.connections[coil_num-1]).upper(),'timer':3,'transition':2})
               
                #set the display text script
                self.game.score_display.set_script(script)
                    
                

	def process_auto(self):
		if (self.action == 'repeat'):
                    self.item.pulse()
                    #self.set_matrix()
                elif (self.action == 'auto'):
                    self.change_item()
                    self.item.pulse()
                    #self.set_matrix()
                    if (self.iterator < self.max):
			self.iterator += 1
                    else:
                        self.iterator =0
		self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)


#        def set_matrix(self):
#            #update matrix to show active coil
#            num =self.item.number-32
#            self.log.info('coil number is:%s',num)
#            bank= num/8
#            drive = num%8
#            self.matrix_layer.target_x = 105+(bank*5)
#            self.matrix_layer.target_y = 7+(drive*3)
#
#            #clear matrix display after set time
#            self.delay(name='clear_matrix', event_type=None, delay=1, handler=self.clear_matrix)
#
#        def clear_matrix(self):
#            self.matrix_layer.target_x = 128
#            self.matrix_layer.target_y = 32


	def sw_enter_active(self,sw):
            if self.game.switches.direction.is_active():
		if (self.action == 'manual'):
			self.action = 'repeat'
			if self.game.lamps.has_key('start'): self.game.lamps.start.disable()
			#self.instruction_layer.set_text(' - Repeat')
                        self.game.score_display.set_text(text=str(' - Repeat').upper(),row=0,justify='right',opaque=False)
		elif (self.action == 'repeat'):
			self.action = 'auto'
			if self.game.lamps.has_key('start'): self.game.lamps.start.disable()
			#self.instruction_layer.set_text(' - Auto')
                        self.game.score_display.set_text(text=str(' - Auto').upper(),row=0,justify='right',opaque=False)
                elif (self.action == 'auto'):
			self.action = 'manual'
			if self.game.lamps.has_key('start'): self.game.lamps.start.schedule(schedule=0xff00ff00, cycle_seconds=0, now=False)
			#self.instruction_layer.set_text(' - Manual')
                        self.game.score_display.set_text(text=str(' - Manual').upper(),row=0,justify='right',opaque=False)
                        #self.cancel_delayed('repeat')
		return True
            elif self.game.switches.direction.is_inactive():
                self.item.disable()
                self.game.modes.remove(self)
                return True


	def sw_start_active(self,sw):
		if (self.action == 'manual'):
			self.item.pulse(20)
                        #self.set_matrix()
		return True


class SwitchTest(ServiceModeSkeleton):
	"""Switch Test"""
	def __init__(self, game, priority, font, big_font):
		super(SwitchTest, self).__init__(game, priority,font)
		self.name = "Switch Test"
#                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/switch_test_bgnd.dmd').frames[0])
#		self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
#                self.matrix_layer.composite_op = "blacksrc"
#                self.matrix_layer.target_x = 128
#                self.matrix_layer.target_y = 32
#                self.title_layer = dmd.TextLayer(1, 0, font, "left")
#		self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
#                self.row_layer = dmd.TextLayer(1, 18, font, "left")
#                self.column_layer = dmd.TextLayer(1, 24, font, "left")
#                self.number_layer = dmd.TextLayer(99, 24, font, "right")
#		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.item_layer, self.row_layer,self.column_layer,self.number_layer,self.matrix_layer])

                #connector setup
                self.base_colour =['White','Green']
                self.connector_key = [6,8]

                #populate connector colours
                for j in range (len(self.base_colour)):
                    self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White']
                    colour_set = self.colours
                    colour_set.pop(self.connector_key[j]-1)
                    for i in range(len(colour_set)):
                        if colour_set[i]==self.base_colour[j]:
                         colour_set[i] = "Black"
                    if j==0:
                        self.row_colour = colour_set
                    elif j==1:
                        self.col_colour = colour_set
               

                self.direct_colours = ['Green','Brown','Red','Orange','Yellow','Black','Blue','Purple','Grey','Green','','']
                
		for switch in self.game.switches:
			if self.game.machine_type == 'sternWhitestar':
				add_handler = 1
			elif switch != self.game.switches.exit:
				add_handler = 1
			else:
				add_handler = 0
			if add_handler:
				self.add_switch_handler(name=switch.name, event_type='inactive', delay=None, handler=self.switch_handler)
				self.add_switch_handler(name=switch.name, event_type='active', delay=None, handler=self.switch_handler)

	def switch_handler(self, sw):
		if (sw.state):
                    self.game.sound.play('service_switch_edge')

		#self.item_layer.set_text(str(sw.label))
                #clear any active display scripts
                self.game.score_display.cancel_script()
                script = []

                if sw.yaml_number.count('S')>0 and sw.yaml_number.count('D')==0 and sw.yaml_number.count('F')==0:
                    matrix =[]
                    matrix.append(int(sw.yaml_number[1])-1)
                    matrix.append(int(sw.yaml_number[2])-1)
                    self.log.debug(matrix)
                    
                    row_colour = self.base_colour[0]+'/'+self.row_colour[int(matrix[1])]
                    col_colour = self.base_colour[1]+'/'+self.col_colour[int(matrix[0])]

                    sw_num = 32+ 16*int(matrix[0])+int(matrix[1])
                    #self.row_layer.set_text(row_colour)
                    #self.column_layer.set_text(col_colour)
                    #self.number_layer.set_text(sw.yaml_number)
                    
                    script.append({'top':str(sw.yaml_number+' '+sw.label[:12]).upper(),'bottom':str('Row: '+row_colour).upper(),'timer':3,'transition':2})
                    script.append({'top':str(sw.yaml_number+' '+sw.label[:12]).upper(),'bottom':str('Col: '+col_colour).upper(),'timer':3,'transition':2})
                    
                
#                    if sw.state:
#                        self.matrix_layer.target_x = 102+int(matrix[0])*3
#                        self.matrix_layer.target_y = 3+int(matrix[1])*3
#                    else:
#                        self.matrix_layer.target_x = 128
#                        self.matrix_layer.target_y = 32

                else:
                    sw_num = sw.number
                    row_colour = self.direct_colours[sw_num-8]
                    #self.row_layer.set_text(row_colour)
                    #self.column_layer.set_text("")
                    #self.number_layer.set_text("sd"+str(sw_num))
                    script.append({'top':('SD'+str(sw_num)+' '+sw.label[:12]).upper(),'bottom':str('Row: '+row_colour).upper(),'timer':3,'transition':2})

                #set the display text script
                self.game.score_display.set_script(script)
		return True


        def mode_stopped(self):
                super(SwitchTest, self).mode_stopped()
                self.game.score_display.cancel_script()
                
                
	def sw_enter_active(self,sw):
            if self.game.switches.direction.is_active():
		return True
            elif self.game.switches.direction.is_inactive():
                self.game.modes.remove(self)
                return True


class Statistics(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, name, itemlist):
		super(Statistics, self).__init__(game, priority,font)

		self.name = name
		self.items = []
                audits_list = self.game.displayed_audits
                
		#for section in sorted(itemlist.iterkeys()):
                for audits_section in audits_list.iterkeys():
                    self.log.info("Stats Section:"+str(audits_section))
                    self.items.append( AuditDisplay( self.game, priority + 1, font, big_font, section_key=audits_section,itemlist =audits_list[audits_section] ))
                                

class AuditDisplay(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, section_key, itemlist):
		super(AuditDisplay, self).__init__(game, priority, font)
		
                self.name = itemlist['label'] #name of section is set as a label, so the key is seperate

           	self.items = []
		for item in sorted(itemlist.iterkeys()):
                    if item!='label':
                        self.log.info("Stats Item:"+str(item))
                        audit_value = audits.display(self.game,section_key,item) #calc the required value from the audits database. formating is also handled in the audits class
                        self.items.append( AuditItem(str(itemlist[item]['label']).upper(), audit_value))


	def mode_started(self):
		super(AuditDisplay, self).mode_started()

	def change_item(self):
		super(AuditDisplay, self).change_item()
                self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                    

	def sw_enter_active(self, sw):
            if self.game.switches.direction.is_active():
		return True
            elif self.game.switches.direction.is_inactive():
                self.item.disable()
                self.game.modes.remove(self)
                return True


            
#class AuditsDisplay(ServiceMode):
#
#	def __init__(self, game, priority, section_key, itemlist):
#		super(AuditsDisplay, self).__init__(game=game, priority=priority)
#                self.log = logging.getLogger('core.serviceAuditsDisplayer')
#                self.section_key  = section_key
#                self.itemlist = itemlist
#                self.title=itemlist['label']
#                self.position = 0
#                self.bottom_range = 0
#                self.top_range = 9
#                self.hilight_index = 0
#
#                #vars for editing record
#                self.edit = False
#                self.options_list = []
#                self.options_index = 0
#                self.option_index_start_posn_set = False
#
#        def increment(self,inc):
#                self.position+=inc
#
#                #adjust the hilight index for displaying in row of 10
#                if self.hilight_index>=9 and inc>0:
#                    self.hilight_index=9
#                elif self.hilight_index<=0 and inc<0:
#                    self.hilight_index=0
#                else:
#                    self.hilight_index+=inc
#
#                #increasing
#                if self.position>len(self.itemlist): #rollround
#                    self.position = 0
#                    self.hilight_index = 0
#                    self.bottom_range = 0
#                    self.top_range = 9
#
#                elif self.position>self.top_range: #move list range
#                    self.bottom_range +=1
#                    self.top_range +=1
#
#                #descreasing
#                if self.position<0: #rollround
#                    self.position = len(self.itemlist)-1
#                    self.hilight_index = 9
#                    self.bottom_range = len(self.itemlist)-10
#                    self.top_range = len(self.itemlist)
#
#                elif self.position<self.bottom_range: #move list range
#                    self.bottom_range -=1
#                    self.top_range -=1
#
#
#                #play sound
#                self.game.sounds.serviceLeft.play()
#                #debug
#                self.log.info("Bottom range index is:%s",self.bottom_range)
#                self.log.info("Top range index is:%s",self.top_range)
#                self.log.info("Hilight index is:%s",self.hilight_index)
#                self.log.info("Position index is:%s",self.position)
#                #update display
#                self.set_layer_needs_update()
#
#
#	def sw_flipperLwL_active(self, sw):
#
#            self.increment(-1)
#
#            return procgame.game.SwitchStop
#
#	def sw_flipperLwR_active(self, sw):
#
#            self.increment(1)
#            return procgame.game.SwitchStop
#
#
#        def get_option_index(self,list,value): #determine the start index for the optinos list when first editing
#            #debug
#            self.log.info("list passed:%s, value passed:%s, list length:%s",list,value,len(list)-1)
#
#            if self.option_index_start_posn_set==False:
#                for i in range(len(list)):
#                    if list[i]==value:
#                        self.option_index_start_posn_set = True
#                        return i
#            else:
#               return self.options_index
#
#
#        def inc_options(self,inc):
#
#            #update the options position
#            self.options_index+=inc
#
#            #keep index in range
#            if self.options_index>len(self.options_list)-1 :
#                self.options_index=0
#            elif self.options_index<0:
#                self.options_index=len(self.options_list)-1
#
#            #update display
#            self.set_layer_needs_update()
#
#
#        def create_list(self,start,end):
#                inc=0
#                dict = {}
#
#                for item in sorted(self.itemlist.iterkeys()):
#                    if inc>=start and inc<=end and item!='label':
#                        dict[item]=self.itemlist[item]
#                        #self.log.info(item)
#                    inc+=1
#
#                #debug
#                self.log.info("Original List:%s",self.itemlist)
#                self.log.info("Created List:%s",dict)
#                return dict
#
#
#	def layer_info(self):
#                self.date_time = str(strftime("%A, %d %B %Y, %I:%M:%S%p"))
#
#                itemlist = self.create_list(self.bottom_range,self.top_range)
#                menu_data =[]
#
#                #iterate though list keys
#                for item in sorted(itemlist.iterkeys()):
#
#                        value = audits.display(self.game,self.section_key,item)
#                        #create menu display data
#                        menu_data.append({'title':str(itemlist[item]['label']),'setting':value,'default':value})
#                      
#
#                mparams = {'title':self.title,'datetime': self.date_time,'data':menu_data,'index':self.hilight_index,'edit':0}
#                self.log.info('Menu Data:%s',mparams)
#
#                #send the info to the content layer
#                return ('service-main_r1', mparams)
            
class StatsDisplay(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, name, itemlist):
		super(StatsDisplay, self).__init__(game, priority, font)
		self.name = name

                self.item_layer = dmd.TextLayer(1, 11, font, "left")
                self.value_layer = dmd.TextLayer(127, 11, big_font, "right")
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer])

		self.items = []
		for item in sorted(itemlist.iterkeys()):
                    #self.log.info("Stats Item:"+str(item))
                    if type(itemlist[item])==type({}):
			self.items.append( HighScoreItem(str(item), itemlist[item]['inits'], itemlist[item]['score']) )
                    else:
			self.items.append( StatsItem(str(item), itemlist[item]) )

		
	def mode_started(self):
		super(StatsDisplay, self).mode_started()

	def change_item(self):
		super(StatsDisplay, self).change_item()
		try:
			self.item.score
		except:
			self.item.score = 'None'

		if self.item.score == 'None':
			self.value_layer.set_text(str(self.item.value))
		else:
			self.value_layer.set_text(self.item.value + ": " + str(self.item.score))

	def sw_enter_active(self, sw):
            if self.game.switches.direction.is_active():
		return True
            elif self.game.switches.direction.is_inactive():
                self.item.disable()
                self.game.modes.remove(self)
                return True
            

class AuditItem:
	"""Service Mode."""
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def disable(self):
		pass

class HighScoreItem:
	"""Service Mode."""
	def __init__(self, name, value, score):
		self.name = name
		self.value = value
		self.score = score

	def disable(self):
		pass


class Settings(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, name, itemlist):
		super(Settings, self).__init__(game, priority,font)
		#self.title_layer.set_text('Settings')
		self.name = name
		self.items = []
		self.font = font
		for section in sorted(itemlist.iterkeys()):
			self.items.append( SettingsEditor( self.game, priority + 1, font, big_font, str(section),itemlist[section] ))

class SettingsEditor(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, name, itemlist):
		super(SettingsEditor, self).__init__(game, priority, font)
#                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_adjust_bgnd.dmd').frames[0])
#		self.title_layer = dmd.TextLayer(1, 0, font, "left")
#		self.item_layer = dmd.TextLayer(1, 11, font, "left")
#		self.instruction_layer = dmd.TextLayer(1, 25, font, "left")
#                self.instruction_layer.composite_op = "blacksrc"
#		self.no_exit_switch = game.machine_type == 'sternWhitestar'
		#self.title_layer.set_text('Settings')
		self.name = name
		self.items = []
#		self.value_layer = dmd.TextLayer(127, 11, big_font, "right")
#		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer, self.instruction_layer])
		for item in itemlist.iterkeys():
			#self.items.append( EditItem(str(item), itemlist[item]['options'], itemlist[item]['value'] ) )
			if 'increments' in itemlist[item]:
				num_options = (itemlist[item]['options'][1]-itemlist[item]['options'][0]) / itemlist[item]['increments']
				option_list = []
				for i in range(0,int(num_options)):
					option_list.append(itemlist[item]['options'][0] + (i * itemlist[item]['increments']))
				self.items.append( EditItem(str(item), option_list, self.game.user_settings[self.name][item]) )
			else:
				self.items.append( EditItem(str(item), itemlist[item]['options'], self.game.user_settings[self.name][item]) )
		self.state = 'nav'
		self.stop_blinking = True
		self.item = self.items[0]
                
                #add custom code here for display of procgame version match on name?
                #self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                
		self.option_index = self.item.options.index(self.item.value)

	def mode_started(self):
		super(SettingsEditor, self).mode_started()

	def mode_stopped(self):
		self.game.sound.play('service_exit')
                self.game.score_display.reset()


	def sw_enter_active(self, sw):
		if self.game.switches.direction.is_active():
                    self.process_enter()
                elif self.game.switches.direction.is_inactive():
                    self.process_exit()
                return True


	def process_enter(self):
		if self.state == 'nav':
			self.state = 'edit'
			self.blink = True
			self.stop_blinking = False
			self.delay(name='blink', event_type=None, delay=.3, handler=self.blinker)
		else:
			self.state = 'nav'
			self.game.sound.play('service_save')
			self.game.user_settings[self.name][self.item.name]=self.item.value
			self.stop_blinking = True
                        self.item.value = self.item.options[self.option_index]
			self.game.save_settings()
                        
                        #self.instruction_layer.set_text("Saved")
                        self.game.score_display.set_text(text="Saved".upper(),row=1,justify='left',opaque=False)
                        self.delay(name='change_complete', event_type=None, delay=1, handler=self.change_complete)

#	def sw_exit_active(self, sw):
#		self.process_exit()
#		return True

	def process_exit(self):
		if self.state == 'nav':
			self.game.modes.remove(self)
		else:
			self.state = 'nav'
			#self.value_layer.set_text(str(self.item.value))
                        self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
			self.stop_blinking = True
			self.game.sound.play('service_cancel')
			
                        #self.instruction_layer.set_text("Change cancelled")
                        self.game.score_display.set_text(text="Cancel".upper(),row=1,justify='left',opaque=False)
                        self.delay(name='change_complete', event_type=None, delay=1, handler=self.change_complete)
			
	
        def sw_step_active(self,sw):
		if self.game.switches.direction.is_active():
			self.process_up()

		elif self.game.switches.direction.is_inactive():
			self.process_down()
                        
		return True

	def process_up(self):
		if self.state == 'nav':
			self.item.disable()
			if (self.iterator < self.max):
				self.iterator += 1
                        else:
                            self.iterator =0

			self.game.sound.play('service_next')
			self.change_item()
		else:
			if self.option_index < (len(self.item.options) - 1):
				self.option_index += 1
				#self.item.value = self.item.options[self.option_index]
				#self.value_layer.set_text(str(self.item.value))
                                #self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                                self.game.score_display.set_text(text=str(self.item.options[self.option_index]).upper(),row=1,justify='right',opaque=True)
				

	def process_down(self):
		if self.state == 'nav':
			self.item.disable()
			if (self.iterator > 0):
				self.iterator -= 1
                        else:
                            self.iterator =self.max
                            
			self.game.sound.play('service_previous')
			self.change_item()
		else:
			if self.option_index > 0:
				self.option_index -= 1
				#self.item.value = self.item.options[self.option_index]
				#self.value_layer.set_text(str(self.item.value))
                                #self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                                self.game.score_display.set_text(text=str(self.item.options[self.option_index]).upper(),row=1,justify='right',opaque=True)
				
	def change_item(self):
		ctr = 0
                for item in self.items:
			if ctr == self.iterator:
				self.item = item
			ctr += 1
		self.max = ctr - 1
		#self.item_layer.set_text(self.item.name)
		#self.value_layer.set_text(str(self.item.value))
                self.game.score_display.set_text(text=str(self.item.name).upper(),row=0,justify='left',opaque=True)
                self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
		self.option_index = self.item.options.index(self.item.value)
			
	def disable(self):
		pass

	def blinker(self):
		if self.blink: 
			#self.value_layer.set_text(str(self.item.value))
                        #self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                        self.game.score_display.set_text(text=str(self.item.options[self.option_index]).upper(),row=1,justify='right',opaque=True)	
			self.blink = False
		else:
			#self.value_layer.set_text("")
                        self.game.score_display.set_text(text="",row=1,justify='right',opaque=True)
                        
			self.blink = True
		if not self.stop_blinking:
			self.delay(name='blink', event_type=None, delay=.3, handler=self.blinker)
		#else:
			#self.value_layer.set_text(str(self.item.value))
                        #self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                        #self.game.score_display.set_text(text=str(self.item.options[self.option_index]).upper(),row=1,justify='right',opaque=True)
				
	
	def change_complete(self):
		#self.instruction_layer.set_text("")
                self.game.score_display.set_text(text=str(self.item.value).upper(),row=1,justify='right',opaque=True)
                
		
class EditItem:
	"""Service Mode."""
	def __init__(self, name, options, value):
		self.name = name
		self.options = options
		self.value = value

	def disable(self):
		pass

#mode for coin door opening & showing game health
class CoinDoor(game.Mode):

	def __init__(self, game):
		super(CoinDoor, self).__init__(game, priority=999)

                self.log = logging.getLogger('whirlwind.coindoor')
		self.name = "Coin Door"
        
                self.sound_repeats = 3
               

        def reset(self):
                self.sound_counter = 0

	def mode_started(self):
		super(CoinDoor, self).mode_started()

                #reset
                self.reset()

                #load messages for status label
                self.load_messages()

                #play sound
                self.play_sound()


        def mode_stopped(self):
                super(CoinDoor, self).mode_stopped()

                #cancel update loops
                self.cancel_delayed(self.sound_repeat_delay)
                self.game.score_display.cancel_script()
                
                #reload attract display
                self.game.attract_mode.attract_display()

        def play_sound(self):
                #play sound
                timer=0.5
                self.game.sound.play('service_alert')
                self.sound_counter+=1
                self.sound_repeat_delay = self.delay(delay=timer,handler=self.play_sound)
                if self.sound_repeats == self.sound_counter:
                    self.cancel_delayed(self.sound_repeat_delay)


        def load_messages(self):       
                self.game.score_display.cancel_script()
                script=[]
                #set text for the layers
                script.append({'top':'Coin Door Open'.upper(),'bottom':'High Voltage Off'.upper(),'timer':5,'transition':3})
                
                script.append({'top':str(self.game.system_name),'bottom':'OCS Ltd 2015'.upper(),'timer':3,'transition':2})
                script.append({'top':str(self.game.system_name),'bottom':str('v'+self.game.system_version).upper(),'timer':3,'transition':2})
                script.append({'top':str(self.game.system_name),'bottom':'Press "ENTER"'.upper(),'timer':3,'transition':2})
               
                if self.game.health_status =='OK' or self.game.health_status =='':
                    script.append({'top':str(self.game.system_name),'bottom':'No Errors'.upper(),'timer':3,'transition':2})
               
                elif self.game.health_status =='ERRORS':
                    for error in sorted(self.game.switch_error_log):
                        script.append({'top':'Check Switch: '.upper(),'bottom':str(error).upper(),'timer':3,'transition':2})
               
                self.game.score_display.set_script(script)


	def sw_coinDoorClosed_active(self, sw):
		self.game.modes.remove(self)
        
       