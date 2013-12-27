import logging
import locale
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
                self.log = logging.getLogger('testrig.service')
		self.name = ""
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
		self.title_layer = dmd.TextLayer(1, 0, font, "left")
		self.item_layer = dmd.TextLayer(128/2, 11, font, "center")
		self.instruction_layer = dmd.TextLayer(1, 25, font, "left")
                self.instruction_layer.composite_op = "blacksrc"
		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.instruction_layer])
		self.no_exit_switch = game.machine_type == 'sternWhitestar'

	def mode_started(self):
		self.title_layer.set_text(str(self.name))
		self.game.sound.play('service_enter')

	def mode_stopped(self):
		self.game.sound.play('service_exit')

	def disable(self):
		pass

	def sw_down_active(self, sw):
		if self.game.switches.enter.is_active():
			self.game.modes.remove(self)
			return True

	def sw_exit_active(self, sw):
		self.game.modes.remove(self)
		return True

class ServiceModeList(ServiceModeSkeleton):
	"""Service Mode List base class."""
	def __init__(self, game, priority, font):
		super(ServiceModeList, self).__init__(game, priority, font)
		self.items = []

	def mode_started(self):
		super(ServiceModeList, self).mode_started()

		self.iterator = 0
		self.change_item()

	def change_item(self):
		ctr = 0
                for item in self.items:
			if (ctr == self.iterator):
				self.item = item
			ctr += 1
		self.max = ctr - 1
		self.item_layer.set_text(self.item.name)

	def sw_up_active(self,sw):
		if self.game.switches.enter.is_inactive():
			self.item.disable()
			if (self.iterator < self.max):
				self.iterator += 1
                        else:
                            self.iterator =0
			self.game.sound.play('service_next')
			self.change_item()
		return True

	def sw_down_active(self,sw):
		if self.game.switches.enter.is_inactive():
			self.item.disable()
			if (self.iterator > 0):
				self.iterator -= 1
                        else:
                            self.iterator =self.max
			self.game.sound.play('service_previous')
			self.change_item()
		elif self.no_exit_switch:
			self.exit()
		return True

	def sw_enter_active(self,sw):
		self.game.modes.add(self.item)
		return True

	def exit(self):
		self.item.disable()
		self.game.modes.remove(self)
		return True

class ServiceMode(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font,big_font, extra_tests=[]):
		super(ServiceMode, self).__init__(game, priority,font)
		#self.title_layer.set_text('Service Mode')
		self.name = 'Service Mode'
		self.tests = Tests(self.game, self.priority+1, font, big_font, extra_tests)
		self.items = [self.tests]
		if len(self.game.settings) > 0: 
			self.settings = Settings(self.game, self.priority+1, font, big_font, 'Settings', self.game.settings)
			self.items.append(self.settings)


		if len(self.game.game_data) > 0: 
			self.statistics = Statistics(self.game, self.priority+1, font, big_font, 'Statistics', self.game.game_data)
			self.items.append(self.statistics)

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
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/switch_test_bgnd.dmd').frames[0])
		self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                self.matrix_layer.composite_op = "blacksrc"
                self.matrix_layer.target_x = 128
                self.matrix_layer.target_y = 32
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
                self.instruction_layer = dmd.TextLayer(45, 0, font, "left")
		self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
                self.board_layer = dmd.TextLayer(1, 18, font, "left")
                self.drive_layer = dmd.TextLayer(1, 24, font, "left")
                self.row_layer = dmd.TextLayer(1, 18, font, "left")
                self.column_layer = dmd.TextLayer(1, 24, font, "left")
                self.number_layer = dmd.TextLayer(99, 24, font, "right")
		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.instruction_layer,self.item_layer, self.row_layer,self.column_layer,self.number_layer,self.matrix_layer])

                #connector setup
                self.base_colour =['Red','Grey']
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
                self.instruction_layer.set_text(' - Repeat')

                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_repeat)

        def mode_stopped(self):
                self.cancel_delayed('repeat')

	def change_item(self):
		super(LampTest, self).change_item()

                 #get the yaml numbering data for coils
                self.lamp_data =self.item.yaml_number.split(':')
                self.lamp_col_data = self.lamp_data[0].split("-")
                self.lamp_row_data = self.lamp_data[1].split("-")

                self.log.info("PDB Lamp Data:"+str(self.lamp_data))
                self.lamp_num = int(self.lamp_row_data[3])+8*int(self.lamp_col_data[3])+1
                self.log.info("Lamp No:"+str(self.lamp_num))

                #set text for the layers
                self.item_layer.set_text(self.item.label)
                self.row_layer.set_text(self.base_colour[0]+' '+self.row_colour[int(self.lamp_row_data[3][-1:])])
                self.column_layer.set_text(self.base_colour[1]+' '+self.col_colour[int(self.lamp_col_data[3][-1:])])
                self.board_layer.set_text("PDB Board "+self.lamp_col_data[0][-1:])
                self.drive_layer.set_text("Row Bank "+self.lamp_row_data[1][-1:]+ " Col Bank"+self.lamp_col_data[1][-1:])
                self.number_layer.set_text("L"+str(self.lamp_num))

		self.item.schedule(schedule=0x00ff00ff, cycle_seconds=0, now=True)
                self.process_repeat()

        def process_repeat(self):
		self.set_matrix()
		self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_repeat)

        def set_matrix(self):
            #update matrix to show active coil
            self.matrix_layer.target_x = 102+int(self.lamp_col_data[3][-1:])*3
            self.matrix_layer.target_y = 3+int(self.lamp_row_data[3][-1:])*3

            #clear matrix display after set time
            self.delay(name='clear_matrix', event_type=None, delay=1, handler=self.clear_matrix)

        def clear_matrix(self):
            self.matrix_layer.target_x = 128
            self.matrix_layer.target_y = 32


	def sw_enter_active(self,sw):
		return True


class CoilTest(ServiceModeList):
	"""Coil Test"""
	def __init__(self, game, priority, font, big_font):
		super(CoilTest, self).__init__(game, priority, font)
		#set mode name
                self.name = "Coil Test"

                #setup layers
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/coil_test_bgnd.dmd').frames[0])
		self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                self.matrix_layer.composite_op = "blacksrc"
                self.matrix_layer.target_x = 128
                self.matrix_layer.target_y = 32
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
		self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
                self.instruction_layer = dmd.TextLayer(45, 0, font, "left")
                self.board_layer = dmd.TextLayer(1, 18, font, "left")
                self.drive_layer = dmd.TextLayer(1, 24, font, "left")
                self.conn_layer = dmd.TextLayer(110, 24, font, "right")
		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.item_layer, self.board_layer,self.drive_layer,self.conn_layer,self.instruction_layer,self.matrix_layer])

                #setup mode lists
                self.colours = ['Brown','Red','Orange','Yellow','Green','Blue','Purple','Grey','White']
                self.bank_a_colour = 'Brown'
                self.bank_b_colour = 'Purple'
                self.bank = ['a','b']
                self.connector_key =[2,3]
                self.connections=['J7-1','J7-3','J7-4','J7-5','J7-6','J7-7','J7-8','J7-9','J11-1','J11-2','J11-4','J11-5','J11-6','J11-7','J11-8','J11-9']

		self.items = self.game.coils
                    
		self.max = len(self.items)
                self.log.info("Max:"+str(self.max))

	def mode_started(self):
		super(CoilTest, self).mode_started()
		self.action = 'manual'
                self.instruction_layer.set_text(' - Manual')

                #check this line is needed
		if self.game.lamps.has_key('start'): self.game.lamps.start.schedule(schedule=0xff00ff00, cycle_seconds=0, now=False)

                self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)

        def mode_stopped(self):
                self.cancel_delayed('repeat')

        def change_item(self):
                self.log.info("items total:"+str(len(self.items)))
		ctr = 0
                for item in self.items:
                    if (ctr == self.iterator):
                        self.item = item

                    ctr += 1
                    self.log.info("item:"+str(item.label))
                 #for i in range(len(self.items)):
#                    if i==self.iterator:
#                        self.item = self.items[i]
                #self.item = self.items[self.iterator]

		#self.max = ctr - 1
		self.item_layer.set_text(self.item.label)
                self.log.info("iterator:"+str(self.iterator))

                #get the yaml numbering data for coils
                coil_data =self.item.yaml_number.split('-')
                self.log.info("PDB Coil Data:"+str(coil_data))
                coil_num = int(coil_data[2][-1:])+8*int(coil_data[1][-1:])
                self.log.info("Coil No:"+str(coil_num))

                #set text for the layers
                self.board_layer.set_text("PDB Board "+coil_data[0][-1:])
                self.drive_layer.set_text("Bank "+self.bank[int(coil_data[1][-1:])]+ " Q"+coil_data[2][-1:]+" Sol"+str(coil_num))
                self.conn_layer.set_text(self.connections[coil_num])
                

	def process_auto(self):
		if (self.action == 'repeat'):
                    self.item.pulse()
                    self.set_matrix()
                elif (self.action == 'auto'):
                    self.change_item()
                    self.item.pulse()
                    self.set_matrix()
                    if (self.iterator < self.max):
			self.iterator += 1
                    else:
                        self.iterator =0
		self.delay(name='repeat', event_type=None, delay=2.0, handler=self.process_auto)


        def set_matrix(self):
            #update matrix to show active coil
            coil_data =self.item.yaml_number.split('-')
            bank= coil_data[1][-1:]
            drive = coil_data[2][-1:]
            self.matrix_layer.target_x = 115+int(bank)*6
            self.matrix_layer.target_y = 7+int(drive)*3

            #clear matrix display after set time
            self.delay(name='clear_matrix', event_type=None, delay=1, handler=self.clear_matrix)

        def clear_matrix(self):
            self.matrix_layer.target_x = 128
            self.matrix_layer.target_y = 32


	def sw_enter_active(self,sw):
		if (self.action == 'manual'):
			self.action = 'repeat'
			if self.game.lamps.has_key('start'): self.game.lamps.start.disable()
			self.instruction_layer.set_text(' - Repeat')
		elif (self.action == 'repeat'):
			self.action = 'auto'
			if self.game.lamps.has_key('start'): self.game.lamps.start.disable()
			self.instruction_layer.set_text(' - Auto')
                elif (self.action == 'auto'):
			self.action = 'manual'
			if self.game.lamps.has_key('start'): self.game.lamps.start.schedule(schedule=0xff00ff00, cycle_seconds=0, now=False)
			self.instruction_layer.set_text(' - Manual')
                        #self.cancel_delayed('repeat')
		return True

	def sw_start_active(self,sw):
		if (self.action == 'manual'):
			self.item.pulse(20)
                        self.set_matrix()
		return True


class SwitchTest(ServiceModeSkeleton):
	"""Switch Test"""
	def __init__(self, game, priority, font, big_font):
		super(SwitchTest, self).__init__(game, priority,font)
		self.name = "Switch Test"
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/switch_test_bgnd.dmd').frames[0])
		self.matrix_layer = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(game_path+'dmd/matrix_square.dmd').frames[0])
                self.matrix_layer.composite_op = "blacksrc"
                self.matrix_layer.target_x = 128
                self.matrix_layer.target_y = 32
                self.title_layer = dmd.TextLayer(1, 0, font, "left")
		self.item_layer = dmd.TextLayer(1, 9, big_font , "left")
                self.row_layer = dmd.TextLayer(1, 18, font, "left")
                self.column_layer = dmd.TextLayer(1, 24, font, "left")
                self.number_layer = dmd.TextLayer(99, 24, font, "right")
		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer,self.item_layer, self.row_layer,self.column_layer,self.number_layer,self.matrix_layer])

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

		self.item_layer.set_text(str(sw.label))

                #+'-'+str(sw.number)+''+ ' : ' + str(sw.state)

                if sw.yaml_number.count('/')>0:
                    matrix =sw.yaml_number.split('/')
                    self.log.info(matrix)
                    row_colour = self.base_colour[0]+' '+self.row_colour[int(matrix[1])]
                    col_colour = self.base_colour[1]+' '+self.col_colour[int(matrix[0])]

                    sw_num = 32+ 16*int(matrix[0])+int(matrix[1])
                    self.row_layer.set_text(row_colour)
                    self.column_layer.set_text(col_colour)
                    self.number_layer.set_text("sm"+str(sw_num))
                    if sw.state:
                        self.matrix_layer.target_x = 102+int(matrix[0])*3
                        self.matrix_layer.target_y = 3+int(matrix[1])*3
                    else:
                        self.matrix_layer.target_x = 128
                        self.matrix_layer.target_y = 32

                else:
                    sw_num = sw.number
                    row_colour = self.direct_colours[sw_num-8]
                    self.row_layer.set_text(row_colour)
                    self.column_layer.set_text("")
                    self.number_layer.set_text("sd"+str(sw_num))


		return True

	def sw_enter_active(self,sw):
		return True

class Statistics(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, name, itemlist):
		super(Statistics, self).__init__(game, priority,font)

		self.name = name
		self.items = []
		for section in sorted(itemlist.iterkeys()):
                    self.log.info("Stats Section:"+str(section))
                    if section=='Audits' or section=='Time Stamps':
                        self.items.append( AuditDisplay( self.game, priority + 1, font, big_font, str(section),itemlist[section] ))

class AuditDisplay(ServiceModeList):
	"""Service Mode."""
	def __init__(self, game, priority, font, big_font, name, itemlist):
		super(AuditDisplay, self).__init__(game, priority, font)
		self.name = name

                self.item_layer = dmd.TextLayer(1, 8, font, "left")
                self.value_layer = dmd.TextLayer(1, 16, big_font, "left")
                self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer])

		self.items = []
		for item in sorted(itemlist.iterkeys()):
                    self.log.info("Stats Item:"+str(item))
                    self.items.append( AuditItem(str(item), itemlist[item]) )


	def mode_started(self):
		super(AuditDisplay, self).mode_started()

	def change_item(self):
		super(AuditDisplay, self).change_item()

                if "Time" in self.item.name:
                    self.value_layer.set_text(self.format_time(self.item.value))
                elif "Score" in self.item.name and isinstance(self.item.value, int ):#"Not Set" not in str(self.item.value):
                    self.value_layer.set_text(locale.format("%d",self.item.value,True))
                else:
                    self.value_layer.set_text(str(self.item.value))


	def sw_enter_active(self, sw):
		return True

        def format_time(self,time):
            hrs = int(time/3600)
            mins = int((time-(hrs*3600))/60)
            secs = int(time-(mins*60))

            if hrs>0:
                return str(hrs)+" Hrs "+str(mins)+" Mins"
            else:
                return str(mins)+" Mins "+str(secs)+" Secs"

            

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
                self.bgnd_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load(game_path+'dmd/service_bgnd.dmd').frames[0])
		self.title_layer = dmd.TextLayer(1, 0, font, "left")
		self.item_layer = dmd.TextLayer(1, 11, font, "left")
		self.instruction_layer = dmd.TextLayer(1, 25, font, "left")
                self.instruction_layer.composite_op = "blacksrc"
		self.no_exit_switch = game.machine_type == 'sternWhitestar'
		#self.title_layer.set_text('Settings')
		self.name = name
		self.items = []
		self.value_layer = dmd.TextLayer(127, 11, big_font, "right")
		self.layer = dmd.GroupedLayer(128, 32, [self.bgnd_layer,self.title_layer, self.item_layer, self.value_layer, self.instruction_layer])
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
		self.value_layer.set_text(str(self.item.value))
                
		self.option_index = self.item.options.index(self.item.value)

	def mode_started(self):
		super(SettingsEditor, self).mode_started()

	def mode_stopped(self):
		self.game.sound.play('service_exit')

	def sw_enter_active(self, sw):
		if not self.no_exit_switch:
			self.process_enter()
		return True

	def process_enter(self):
		if self.state == 'nav':
			self.state = 'edit'
			self.blink = True
			self.stop_blinking = False
			self.delay(name='blink', event_type=None, delay=.3, handler=self.blinker)
		else:
			self.state = 'nav'
			self.instruction_layer.set_text("Change saved")
			self.delay(name='change_complete', event_type=None, delay=1, handler=self.change_complete)
			self.game.sound.play('service_save')
			self.game.user_settings[self.name][self.item.name]=self.item.value
			self.stop_blinking = True
			self.game.save_settings()

	def sw_exit_active(self, sw):
		self.process_exit()
		return True

	def process_exit(self):
		if self.state == 'nav':
			self.game.modes.remove(self)
		else:
			self.state = 'nav'
			self.value_layer.set_text(str(self.item.value))
			self.stop_blinking = True
			self.game.sound.play('service_cancel')
			self.instruction_layer.set_text("Change cancelled")
			self.delay(name='change_complete', event_type=None, delay=1, handler=self.change_complete)
			
	def sw_up_active(self, sw):
		if self.game.switches.enter.is_inactive():
			self.process_up()

		else:
			self.process_enter()
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
				self.item.value = self.item.options[self.option_index]
				self.value_layer.set_text(str(self.item.value))
				

	def sw_down_active(self, sw):
		if self.game.switches.enter.is_inactive():
			self.process_down()
		else:
			self.process_exit()
		return True

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
				self.item.value = self.item.options[self.option_index]
				self.value_layer.set_text(str(self.item.value))

	def change_item(self):
		ctr = 0
                for item in self.items:
			if ctr == self.iterator:
				self.item = item
			ctr += 1
		self.max = ctr - 1
		self.item_layer.set_text(self.item.name)
		self.value_layer.set_text(str(self.item.value))
		self.option_index = self.item.options.index(self.item.value)
			
	def disable(self):
		pass

	def blinker(self):
		if self.blink: 
			self.value_layer.set_text(str(self.item.value))
			self.blink = False
		else:
			self.value_layer.set_text("")
			self.blink = True
		if not self.stop_blinking:
			self.delay(name='blink', event_type=None, delay=.3, handler=self.blinker)
		else:
			self.value_layer.set_text(str(self.item.value))
	
	def change_complete(self):
		self.instruction_layer.set_text("")
		
class EditItem:
	"""Service Mode."""
	def __init__(self, name, options, value):
		self.name = name
		self.options = options
		self.value = value

	def disable(self):
		pass
