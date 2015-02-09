import time
import sqlite3
import os
import logging
import json
import yaml

AUDITS_PATH = './var/audits_store.db'
AUDITS_SCHEMA_PATH = './config/audits_catalogue.yaml'
AUDITS_DISPLAY_PATH = './config/audits_display.yaml'

shared_store = None
shared_schema = None

def load(game):
	"""docstring for load"""
	store = get_shared_store(game)

def save(game):
	"""docstring for save"""
	store = get_shared_store(game)
	store.save()

def record_value(game,key, value=1):
	"""Convenience audit-recorder."""
	store = get_shared_store(game)
	store.record(key_path=key, value=value)

def display(game,section_key,key):
	"""Convenience audit display method."""
	store = get_shared_store(game)
	return store.display(section=section_key,name=key)

def update_counter(game,key, value):
	"""Convenience audit-recorder."""
	store = get_shared_store(game)
	store.update_counter(key_path=key, value=value)


def get_shared_store(game):
	global shared_store
	if not shared_store:
		#shared_store = AuditStore(schema=get_shared_schema())
                shared_store = AuditStore(game)
	return shared_store



class AuditStore(object):
	"""docstring for AuditStore"""
	
	audit_ids_by_key_path = None
	
	def __init__(self,game):
		super(AuditStore, self).__init__()
		
		self.audit_ids_by_key_path = {}
                self.log = logging.getLogger('audits')
                self.game=game

                self.config = yaml.load(open(AUDITS_SCHEMA_PATH, 'r'))
                self.display_data = yaml.load(open(AUDITS_DISPLAY_PATH, 'r'))
		
		DATABASE_VERSION = 2
		CREATE_VERSION_TABLE = '''create table if not exists version (version integer)'''
		#CREATE_AUDITS_TABLE = '''create table if not exists audits (id integer primary key, key_path text)'''
		#CREATE_RECORDS_TABLE = '''create table if not exists records (audit_id integer, value integer, timestamp integer)'''
                
                CREATE_CATALOGUE_TABLE = '''CREATE TABLE if not exists catalogue(id integer primary key, name VARCHAR(255) NOT NULL,description TEXT NOT NULL,category varchar(255) not null,value integer not null default 0, UNIQUE (name))'''

                CREATE_DATA_TABLE = '''CREATE TABLE if not exists data(id integer primary key, catalogue_id INTEGER NOT NULL,value INTEGER NOT NULL DEFAULT 0,submitted INTEGER NOT NULL,game_id INTEGER NOT NULL,code_version VARCHAR(10) NOT NULL)'''
                CREATE_DATA_TIMESTAMP_INDEX = '''create index if not exists submitted_index on data(submitted)'''
		CREATE_DATA_CATALOGUE_INDEX = '''create index if not exists catalogue_index on data(catalogue_id)'''

                #CREATE_DISPLAY_TABLE = '''CREATE TABLE if not exists display(id integer primary key, name VARCHAR(255) NOT NULL,description TEXT,type VARCHAR(255) NOT NULL,section VARCHAR(255) NOT NULL,cat_key1 varchar(50) not null,cat_key2 varchar(50),cat_key3 varchar(50),cat_key4 varchar(50),countdown_start INTEGER,order_col INTEGER)'''
                #CREATE_SECTION_TABLE = '''CREATE TABLE if not exists section(id integer primary key, name VARCHAR(255) NOT NULL)'''
                #CREATE_TYPE_TABLE = '''CREATE TABLE if not exists type(id integer primary key, name VARCHAR(255) NOT NULL)'''
                #CREATE_DISPLAY_CATALOGUE_INDEX = '''create index if not exists catalogue_index on display(cat_key1)'''


                self.conn = sqlite3.connect(self.database_path())
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
				logging.getLogger('audits').warning('Audits database version (%d) is not current (%d).  Audits will be reset.', version, DATABASE_VERSION)
				del self.conn
				os.remove(self.database_path())
				return self.load()

                #create tables
		self.conn.execute(CREATE_CATALOGUE_TABLE)
		self.conn.execute(CREATE_DATA_TABLE)
                #self.conn.execute(CREATE_DISPLAY_TABLE)
                #self.conn.execute(CREATE_SECTION_TABLE)
                #self.conn.execute(CREATE_TYPE_TABLE)

                #create indexes
		self.conn.execute(CREATE_DATA_TIMESTAMP_INDEX)
                self.conn.execute(CREATE_DATA_CATALOGUE_INDEX)
                #self.conn.execute(CREATE_DISPLAY_CATALOGUE_INDEX)
		self.conn.commit()

                #load catalogue of audits
                self.update_catalogue()
		logging.getLogger('audits').info('Audits loaded.')
	
	def database_path(self):
		return AUDITS_PATH
	

        def update_catalogue(self):
		"""docstring for apply_schema"""
		
                self.audit_ids_by_key_path = {}

               
                data=[]
               
                categories = ['generalAudits','featureAudits','counters']
                for i in range(len(categories)):
                    for item in self.config[categories[i]]:
                        item_dict = self.config[categories[i]][item]
                        #self.log.debug(item)
                        data.append({'name':item,'label':item_dict['label'],'category':categories[i]})

                switches = self.game.switches
                for switch in switches:
                    #self.log.debug(switch.name)
                    data.append({'name':str(switch.name)+str('SwHit'),'label':str(switch.label)+str(' Switch Hit'),'category':'switchAudits'})


                for item in data:
                    c = self.conn.cursor()
                    c.execute('''select id from catalogue where name=?''', (item['name'],))
                    result = c.fetchone()
                    if not result: # Audit is not already in the database.
                        self.log.info('Adding new audit catalogue entry: %s',item['name'])
                        c.execute('''insert into catalogue(name,description,category) values (?,?,?)''', (item['name'],item['label'],item['category']))
                        self.audit_ids_by_key_path[item['name']] = c.lastrowid
                    else:
                        self.audit_ids_by_key_path[item['name']] = result[0]
                        
                self.conn.commit()
	
	def record(self, key_path, value):
		#check if key exists in catalogue
                self.check_valid(key_path)

                #setup the data to store
		audit_id = self.audit_ids_by_key_path[key_path]
		value = int(value)
		timestamp = int(time.time())
                game_id=0
                software_version = self.game.system_version

                #create a connection
                c = self.conn.cursor()

                #set the game id
                if key_path!='bootUp':
                    c.execute('''select data.id from data left join catalogue on catalogue.id=data.catalogue_id where catalogue.name='bootUp' order by data.id desc''')
                    result = c.fetchone()
                    game_id= result[0]

                #insert the data
		c.execute('''insert into data(catalogue_id,value,submitted,game_id,code_version) values (?,?,?,?,?)''', (audit_id, value, timestamp, game_id, software_version))
                self.conn.commit()



        def update_counter(self, key_path, value):
		#check if key exists in catalogue
                self.check_valid(key_path)

                #setup the data to store
		cat_id = self.audit_ids_by_key_path[key_path]
		value = int(value)

                #update the cat record
                c = self.conn.cursor()
                c.execute("update catalogue set value=? where id=?",(value,cat_id,))
                self.conn.commit()


	def save(self):
		"""docstring for save"""
		self.conn.commit()
                self.conn.close()

        def check_valid(self,key_path):
             if key_path not in self.audit_ids_by_key_path:
			logging.getLogger('audits').warning('Ignoring unknown audit: %s' % (key_path))
			return
	
	def display(self,section,name):

             

             item = self.display_data[section][name]
             #self.log.debug("audit display method %s",item)

             #extract the main catalogue id
             cat_id1 = self.audit_ids_by_key_path[item['cid1']]

             c = self.conn.cursor()

             if item['type']=='counter':
                #query table to get stored value
                c.execute('''select value from catalogue where id =?''',(cat_id1,))
                result = c.fetchone()
                if not result:
                    return 'Not Set'
                #format result
                value = int(result[0])
               
             elif item['type']=='sum':
                #query table to get stored value
                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id1,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value = int(result[0])

             elif item['type']=='multiSum':
                #extract the additional catalogue id
                cat_id2 = self.audit_ids_by_key_path[item['cid2']]

                #query table to get stored value
                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id1,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value1 = int(result[0])

                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id2,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value2 = int(result[0])

                value=value1+value2

             elif item['type']=='percent':
                #extract the additional catalogue id
                cat_id2 = self.audit_ids_by_key_path[item['cid2']]

                #query table to get stored value
                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id1,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value1 = int(result[0])

                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id2,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value2 = int(result[0])

                value=(value1/value2)*100

             elif item['type']=='average':
                #extract the additional catalogue id
                cat_id2 = self.audit_ids_by_key_path[item['cid2']]

                #query table to get stored value
                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id1,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value1 = int(result[0])

                c.execute('''select sum(value) from data where catalogue_id =?''',(cat_id2,))
                result = c.fetchone()
                if result[0]==None:
                    return 'Not Set'
                #format result
                value2 = int(result[0])

                value=value1/value2

             elif item['type']=='orderFirst':
                #query table to get stored value
                if item['order']=='id':
                    query = '''select value from data where catalogue_id =? order by id'''
                elif item['order']=='date':
                    query = '''select submitted from data where catalogue_id =? order by submitted'''

                c.execute(query,(cat_id1,))
                result = c.fetchone()
                if not result:
                    return 'Not Set'

                #format result
                if item['order']=='id':
                    value =  int(result[0])
                elif item['order']=='date':
                    value = time.strftime("%d %b %Y %I:%M%p",time.localtime(result[0]))

             elif item['type']=='orderLast':
                 #query table to get stored value
                if item['order']=='id':
                    query = '''select value from data where catalogue_id =? order by id desc'''
                elif item['order']=='date':
                    query = '''select submitted from data where catalogue_id =? order by submitted desc'''

                c.execute(query,(cat_id1,))
                result = c.fetchone()
                if not result:
                    return 'Not Set'

                #format result
                if item['order']=='id':
                    value =  int(result[0])
                elif item['order']=='date':
                    value = time.strftime("%d %b %Y %I:%M%p",time.localtime(result[0]))

             #check for format words in keys
             if 'Time' in str(item):
                    value = self.format_time(value)
             elif 'Score' in str(item):
                    value = util.commatize(value)

             #self.log.debug("value returned is:%s",value)
             return value


        def format_time(self,time):
            hrs = int(time/3600)
            mins = int((time-(hrs*3600))/60)
            secs = int(time-(mins*60))

            if hrs>0:
                return str(hrs)+" Hrs "+str(mins)+" Mins"
            else:
                return str(mins)+" Mins "+str(secs)+" Secs"
            
            
        def iter_time_period(self, period, max_count, start=None):
		if not start:
			start = time.time()
		while max_count > 0:
			yield start - period, start
			start -= period
			max_count -= 1
	
	def averages_over_time(self, key_path, period, max_count):
		"""Returns a list of average values, each over the last *period* seconds,
		up to *max_count*
		
		Example::
		
			v = audits.shared_store.averages_over_time(key_path='general:startups',
			                                           period=120, max_count=10)
		"""
		if key_path not in self.audit_ids_by_key_path:
			raise ValueError, 'Given key path is unknown.'
		audit_id = self.audit_ids_by_key_path[key_path]
		output = []
		c = self.conn.cursor()
		for ts_start, ts_end in self.iter_time_period(period, max_count):
			c.execute('''select avg(value) from records where audit_id=? and timestamp >= ? and timestamp < ?''', (audit_id, ts_start, ts_end))
			avg = c.fetchone()[0] or 0
			output.append(int(avg))
		return output
	
	def sums_over_time(self, key_path, period, max_count):
		"""Returns a list of sums, each over the last *period* seconds,
		up to *max_count*"""
		if key_path not in self.audit_ids_by_key_path:
			raise ValueError, 'Given key path is unknown.'
		audit_id = self.audit_ids_by_key_path[key_path]
		output = []
		c = self.conn.cursor()
		for ts_start, ts_end in self.iter_time_period(period, max_count):
			c.execute('''select sum(value) from records where audit_id=? and timestamp >= ? and timestamp < ?''', (audit_id, ts_start, ts_end))
			avg = c.fetchone()[0] or 0
			output.append(int(avg))
		return output


class AuditSchema(object):
	"""docstring for AuditSchema"""
	categories = None
	def __init__(self):
		self.categories = []

class AuditItem(object):
	"""docstring for AuditCategory"""
	name = None
	text = None
	def __init__(self, name, text):
		super(AuditItem, self).__init__()
		self.name = name
		self.text = text

class AuditCategory(AuditItem):
	"""docstring for AuditCategory"""
	audits = None
	def __init__(self, name, text):
		super(AuditCategory, self).__init__(name, text)
		self.audits = []

class Audit(AuditItem):
	"""docstring for Audit"""
	pass


	