def combine(list_1, list_2):
    return [a+b for a, b in zip(list_1, list_2)]


class team_stats:
    def __init__(self, team_data, db):
        print(team_data)
        self.team_id = team_data[0]
        self.player_1 = team_data[1]
        self.player_2 = team_data[2]
        self.team_name = team_data[3]
        
        self.total_meld = 0
        self.total_tricks = 0
        self.total_points = 0
        self.total_count = 0
        
        self.bid_meld = 0
        self.bid_tricks = 0
        self.bid_points = 0
        self.bid_count = 0
        
        self.nonbid_meld = 0
        self.nonbid_tricks = 0
        self.nonbid_points = 0
        self.nonbid_count = 0
        
        self.points_missed = 0
        self.points_missed_tricks = 0
        self.points_missed_count = 0
        self.points_saved = 0
        self.points_saved_tricks = 0
        self.points_saved_count = 0
        
        self.points_denied = 0 
        self.points_denied_tricks = 0 
        self.points_denied_count = 0 
        self.points_allowed = 0
        self.points_allowed_tricks = 0
        self.points_allowed_count = 0
        
        self.db = db

    def __str__(self):
        p_str = (f'({self.team_id=} {self.player_1=} {self.player_2=} {self.team_name=}\n')
        p_str += (f'({self.total_meld=}\n')
        p_str += (f'{self.total_tricks=}\n')
        p_str += (f'{self.total_points=})\n')
        p_str += (f'{self.total_count=})\n\n')
        
        p_str += (f'({self.bid_meld=}\n')
        p_str += (f'{self.bid_tricks=}\n')
        p_str += (f'{self.bid_points=})\n')
        p_str += (f'{self.bid_count=})\n\n')
        
        p_str += (f'({self.nonbid_meld=}\n')
        p_str += (f'{self.nonbid_tricks=}\n')
        p_str += (f'{self.nonbid_points=})\n')
        p_str += (f'{self.nonbid_count=})\n\n')
        
        p_str += (f'{self.points_missed=})\n')
        p_str += (f'{self.points_missed_tricks=})\n')
        p_str += (f'{self.points_missed_count=})\n')
        p_str += (f'{self.points_saved=})\n')
        p_str += (f'{self.points_saved_tricks=})\n')
        p_str += (f'{self.points_saved_count=})\n\n')
        
        p_str += (f'{self.points_denied=})\n')
        p_str += (f'{self.points_denied_tricks=})\n')
        p_str += (f'{self.points_denied_count=})\n')
        p_str += (f'{self.points_allowed=})\n')
        p_str += (f'{self.points_allowed_tricks=})\n')
        p_str += (f'{self.points_allowed_count=})\n\n')
        return p_str
        
    def __repr__(self):
        return str(self)

    def create_str(self, meld, tricks, gained, count, out_of_count):
        def percentage(part, whole):
            return 100 * float(part)/float(whole)

        def fm(num):
            return '{:.2f}'.format(num)

        return_str = f'{fm(meld/count)}, '
        return_str += f'{fm(tricks/count)}, '
        return_str += f'{fm(gained/count)}, '
        return_str += f'{count}, '
        return_str += f'{percentage(count, self.total_count)}%, '
        return_str += f'{percentage(count, out_of_count)}%\n'
        return return_str

    def export_stats(self):
        def fm(num):
            return '{:.2f}'.format(num)
        with open(f'{self.team_name}.csv', 'w') as f:
            save_str = ' , Meld, Tricks, Points Gained, Number of Rounds, Percent of total, Percent of part\n'
            save_str += f'Total points, ' + self.create_str(self.total_meld, self.total_tricks, self.total_points, self.total_count, self.total_count)
            save_str += f'Bid points, ' + self.create_str(self.bid_meld, self.bid_tricks, self.bid_points, self.bid_count, self.total_count)
            save_str += f'Points not taking bid, ' + self.create_str(self.nonbid_meld, self.nonbid_tricks, self.nonbid_points, self.nonbid_count, self.total_count)
            save_str += f'Points missed, ' + self.create_str(self.points_missed, self.points_missed_tricks, 0, self.points_missed_count, self.points_missed_count + self.points_saved_count)
            save_str += f'Points saved, ' + self.create_str(self.points_saved, self.points_saved_tricks, self.points_saved_gained, self.points_saved_count, self.points_missed_count + self.points_saved_count)
            save_str += f'Points denied, ' + self.create_str(self.points_denied, self.points_denied_tricks, 0, self.points_denied_count, self.points_denied_count + self.points_allowed_count)
            save_str += f'Points allowed, ' + self.create_str(self.points_allowed, self.points_allowed_tricks, self.points_allowed_gained, self.points_allowed_count, self.points_denied_count + self.points_allowed_count)
            f.write(save_str)

    def total_meld_data(self):
        def get_team_score(team_num):
            print('Team ID')
            print(self.team_id)
            query_text = (f'SELECT SUM("Meld_{team_num}"), SUM("Tricks_{team_num}"), '
                          f'SUM("Points_Gain_{team_num}"), COUNT("Meld_{team_num}") '
                          f'FROM public."Round" '
                          f'JOIN public."Game" as g_1 ON g_1."G_ID" = "Game_Number" '
                          f'WHERE g_1."Team_{team_num}"={self.team_id} '
                          f'GROUP BY g_1."Team_1", g_1."Team_2"')
            
            stat_data = self.db.execute(query_text)
            print(stat_data)
            if not stat_data:
                return 0, 0, 0, 0
            return [int(i) for i in stat_data]
        
        stats = combine(get_team_score(1), get_team_score(2))
        
        self.total_meld = stats[0]
        self.total_tricks = stats[1]
        self.total_points = stats[2]
        self.total_count = stats[3]

    def bid_meld_data(self):        
        def get_team_score_with_bid(team_num):
            print('STAT data')
            print('Team ID')
            print(self.team_id)
            query_text = (f'SELECT SUM("Meld_{team_num}"), SUM("Tricks_{team_num}"), '
                          f'SUM("Points_Gain_{team_num}"), COUNT("Meld_{team_num}") '
                          f'FROM public."Round" JOIN public."Game" as g_1 ON g_1."G_ID" = "Game_Number" '
                          f'WHERE g_1."Team_{team_num}" = "Team_Bid" AND "Team_Bid"={self.team_id} '
                          f'GROUP BY "Team_Bid", g_1."Team_1", g_1."Team_2" ')
            # print(query_text)
            stat_data = self.db.execute(query_text)
            print(stat_data)
            if not stat_data:
                return 0, 0, 0, 0
            return stat_data

        stats = combine(get_team_score_with_bid(1), get_team_score_with_bid(2))
        self.bid_meld = stats[0]
        self.bid_tricks = stats[1]
        self.bid_points = stats[2]
        self.bid_count = stats[3]

    def nonbid_meld_data(self):        
        def get_team_score_without_bid(team_num):
            print('Team ID')
            print(self.team_id)
            query_text = (f'SELECT SUM("Meld_{team_num}"), SUM("Tricks_{team_num}"), '
                          f'SUM("Points_Gain_{team_num}"), COUNT("Meld_{team_num}") '
                          f'FROM public."Round" JOIN public."Game" as g_1 ON g_1."G_ID" = "Game_Number" '
                          f'WHERE g_1."Team_{team_num}" != "Team_Bid" AND "Team_Bid" != {self.team_id} '
                          f'GROUP BY "Team_Bid", g_1."Team_1", g_1."Team_2" ')
            # print(query_text)
            stat_data = self.db.execute(query_text)
            print(stat_data)
            if not stat_data:
                return 0, 0, 0, 0
            return [int(i) for i in stat_data]
        
        stats = combine(get_team_score_without_bid(1), get_team_score_without_bid(2))
        
        self.nonbid_meld = stats[0]
        self.nonbid_tricks = stats[1]
        self.nonbid_points = stats[2]
        self.nonbid_count = stats[3]
        
    def meld_missed(self):
        def get_missed_meld(team_num, saved=False):
            eq = '<'
            if saved:
                eq = '>='
            other_team = 1
            if team_num == 1:
                other_team = 2

            query_text = (f'SELECT SUM("Meld_{team_num}"), SUM("Tricks_{team_num}"), COUNT("Meld_{team_num}") '
                          f'FROM public."Round" JOIN public."Game" as g_1 ON g_1."G_ID" = "Game_Number" '
                          f'WHERE g_1."Team_{other_team}" = "Team_Bid" AND "Tricks_{team_num}" {eq} 20 AND "Team_Bid" != {self.team_id} '
                          f'GROUP BY "Team_Bid"')  # causes None to not be returned
            stat_data = self.db.execute(query_text)
            if not stat_data:
                return 0, 0, 0
            return [int(i) for i in stat_data]
        
        self.points_missed, self.points_missed_tricks, self.points_missed_count = combine(get_missed_meld(1), get_missed_meld(2))
        self.points_saved, self.points_saved_tricks, self.points_saved_count = combine(get_missed_meld(1, True), get_missed_meld(2, True))
        self.points_saved_gained = self.points_saved + self.points_saved_tricks
        
    def meld_denied(self):
        def get_denied_meld(team_num, denied=False):
            eq = '>='
            if denied:
                eq = '<'
            other_team = 1
            if team_num == 1:
                other_team = 2

            query_text = (f'SELECT SUM("Meld_{team_num}"), SUM("Tricks_{team_num}"), COUNT("Meld_{team_num}") '
                          f'FROM public."Round" JOIN public."Game" as g_1 ON g_1."G_ID" = "Game_Number" '
                          f'WHERE g_1."Team_{other_team}" = "Team_Bid" AND "Tricks_{team_num}" {eq} 20 AND "Team_Bid" = {self.team_id} '
                          f'GROUP BY "Team_Bid"')  # causes None to not be returned
            stat_data = self.db.execute(query_text)
            if not stat_data:
                return 0, 0, 0
            return [int(i) for i in stat_data]
    
        self.points_allowed, self.points_allowed_tricks, self.points_allowed_count = combine(get_denied_meld(1), get_denied_meld(2))
        self.points_allowed_gained = self.points_allowed + self.points_allowed_tricks
        self.points_denied, self.points_denied_tricks, self.points_denied_count = combine(get_denied_meld(1, True), get_denied_meld(2, True))

def calc_stats(db):
    print('stats')
    def get_all_teams():
        query_text = 'SELECT "T_ID", "Player_1", "Player_2", "Friendly_Name" FROM public."Team"'
        teams_data = db.execute(query_text, select_all=True)
        return teams_data
    
    teams = [team_stats(t, db) for t in get_all_teams()]

    for team in teams:
        def important_stats(stats):
            if not stats:
                return 0, 0, 0, 0
            
            return int(stats[0]), int(stats[1]), int(stats[2]), int(stats[3])

        print()
        print()
        print(team)
        team.total_meld_data()
        team.bid_meld_data()
        team.nonbid_meld_data()  
        team.meld_missed()
        team.meld_denied()
        
        print(team)
        team.export_stats()
        # print(team)
    print('Final print')
    print(teams)
    print(len(teams))
