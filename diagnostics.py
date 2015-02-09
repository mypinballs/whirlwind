import time
import sqlite3
import os
import logging
import json
import yaml

DIAGNOSTICS_PATH = './var/diagnostics_store.db'

shared_store = None
shared_schema = None

def load(game):
	"""docstring for load"""
	store = get_shared_store(game)

def update_switches(game, time):
	"""Convenience audit-recorder."""
	store = get_shared_store(game)
	store.update_switches(time=time)

def broken_switches(game):
	"""docstring for save"""
	store = get_shared_store(game)
	result = store.broken_switches()
        return result

def get_shared_store(game):
	global shared_store
	if not shared_store:
                shared_store = DiagnosticsStore(game)
	return shared_store



class DiagnosticsStore(object):
	"""docstring for AuditStore"""
	
	audit_ids_by_key_path = None
	
	def __init__(self,game):
		super(DiagnosticsStore, self).__init__()
		
		self.diagnostic_ids_by_key_path = {}
                self.log = logging.getLogger('diagnostics')
                self.game=game

                #self.config = yaml.load(open(AUDITS_SCHEMA_PATH, 'r'))
                #self.display_data = yaml.load(open(AUDITS_DISPLAY_PATH, 'r'))
		
		DATABASE_VERSION = 1
		CREATE_VERSION_TABLE = '''create table if not exists version (version integer)'''
		 
                CREATE_SWITCH_TABLE = '''CREATE TABLE if not exists switches(id integer primary key, name VARCHAR(255) NOT NULL,description TEXT NOT NULL,value integer not null default 1, UNIQUE (name))'''
                

                self.conn = sqlite3.connect(self.database_path())
                self.conn.text_factory = str #changes enconding to utf-8 not unicode
		self.conn.execute(CREATE_VERSION_TABLE)
		
		# Now check for any existing version information:
		c = self.conn.cursor()
		c.execute('''select version from version limit 1''')
		result = c.fetchone()
		if not result:
			c.execute('''insert into version values (?)''', (DATABASE_VERSION,))
		else:
			(version,) = result
			if version == DATABASE_VERSION:
				pass # we are up to date
			else:
				import pdb; pdb.set_trace()
				self.log.warning('Diagnostics database version (%d) is not current (%d).  Database will be reset.', version, DATABASE_VERSION)
				del self.conn
				os.remove(self.database_path())
				return self.load()

                #create tables
		self.conn.execute(CREATE_SWITCH_TABLE)
		

                #create indexes
		#self.conn.execute(CREATE_DATA_TIMESTAMP_INDEX)
                #self.conn.execute(CREATE_DATA_CATALOGUE_INDEX)
                #self.conn.execute(CREATE_DISPLAY_CATALOGUE_INDEX)
                
		self.conn.commit()

                #load catalogue of audits
                #self.update_catalogue()
		self.log.info('Diagnostics loaded.')
	
	def database_path(self):
		return DIAGNOSTICS_PATH
	

        def update_switches(self,time):
		"""update switches that haven't been activated for passed in no of seconds"""
		
                #self.diagnostic_ids_by_key_path = {}

               
                data=[]
                data_remove = []

                switches = self.game.switches.items_tagged('track_errors')

                for switch in switches:
                    name = str(switch.name)+str('Sw')

                    if switch.time_since_change()>time:
                        data.append({'name':name,'label':str(switch.label)+str(' Switch')})
                    else:
                        data_remove.append({'name':name})

                #add/update all non activated switches
                for item in data:
                    c = self.conn.cursor()
                    c.execute('''select id,value from switches where name=?''', (item['name'],))
                    result = c.fetchone()
                    if not result: # Switch is not in the database.
                        self.log.info('Adding new non-active switch entry: %s',item['name'])
                        c.execute('''insert into switches(name,description) values (?,?)''', (item['name'],item['label']))
                        #self.diagnostic_ids_by_key_path[item['name']] = c.lastrowid
                    else:
                        value=result[1]+1
                        self.log.info('Updating non-active switch entry: %s to %s',item['name'],value)
                        c.execute("update switches set value=? where id=?",(value,result[0],))
                        #self.diagnostic_ids_by_key_path[item['name']] = result[0]

                #remove any activated switches from the table
                for item in data_remove:
                    c = self.conn.cursor()
                    c.execute('''select id from switches where name=?''', (item['name'],))
                    result = c.fetchone()
                    if result:
                        c.execute("delete from switches where id=?",(result[0],))

                #save changes
                self.conn.commit()


        def broken_switches(self):
                level = 10
                c = self.conn.cursor()
                c.execute('''select description from switches where value>=?''', (level,))
                #rs = c.fetchall()
                rs=[rows[0] for rows in c.fetchall()]
                

                if rs:
                    self.game.health_status = 'ERRORS'
                    return rs
                else:
                    self.game.health_status = 'OK'

	