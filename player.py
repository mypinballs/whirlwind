import procgame.game


class Player(procgame.game.Player):

	def __init__(self, name):
		super(Player, self).__init__(name)

                #create player stats
                self.player_stats = {}

                #set player stats defaults
                self.player_stats['status']=''
                self.player_stats['bonus_x']=1
                self.player_stats['skyway_tolls']=1
                self.player_stats['cellar_visits']=0
                self.player_stats['pop_flags']=[0,0,0,0,0,0]
                self.player_stats['lower_super_pops_collected']=0
                self.player_stats['lower_super_pops_level']=0
                self.player_stats['upper_super_pops_collected']=0
                self.player_stats['upper_super_pops_level']=0
                self.player_stats['tornado_level']=0
                self.player_stats['tornados_collected']=0
                self.player_stats['saucers_collected']=0
                self.player_stats['ramps_made']=0
                self.player_stats['compass_flags']=[0,0,0,0,0,0,0,0]
                self.player_stats['compass_level']=1
                self.player_stats['compass_sets_complete']=0
                self.player_stats['letters_collected']=0
                self.player_stats['inlanes_made']=0
                self.player_stats['lock_lit']=False
                self.player_stats['multiball_ready']=False
                self.player_stats['multiball_started']=False
                self.player_stats['multiball_running']=False
                self.player_stats['balls_locked']=0
                self.player_stats['million_lit']=False
                self.player_stats['ball_start_time']=0
                self.player_stats['drop_banks_completed']=0
                self.player_stats['skillshot_level']=1
                self.player_stats['skillshot_in_progress']=False
                self.player_stats['mode_running']=False
                self.player_stats['spinner_level']=0

		