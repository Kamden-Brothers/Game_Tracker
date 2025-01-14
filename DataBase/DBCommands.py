from DataBase import ConnectToDB


def simple_sort(first, second):
    '''
    Places lowest item in first position
    '''
    if first > second:
        return second, first
    return first, second

class DB_Exception(Exception):
    pass

class DBWorker():
    def __init__(self):
        self.con = ConnectToDB.connect_to_db('Pinchole')

    def simple_get(self):
        return

    def get_teams(self):
        '''
        Get all team data
        '''
        with self.con.cursor() as cur:
            cur.execute('''SELECT team_name, p_1.username, p_2.username FROM public.team
                           LEFT JOIN public.player as p_1 on p_1.player_id = team.player_1
                           LEFT JOIN public.player as p_2 on p_2.player_id = team.player_2''')
            return {team[0]: team[1:] for team in cur.fetchall()}

    def get_players(self):
        '''
        Get all player data
        '''
        with self.con.cursor() as cur:
            cur.execute('SELECT username, first_name FROM public.player')
            return {player[0]: player[1:] for player in cur.fetchall()}

    def get_pinochle_matches(self):
        with self.con.cursor() as cur:
            cur.execute('''SELECT game_date, game_of_day, t_1.team_name, t_2.team_name FROM public.game
                           JOIN public.team t_1 ON game.team_1 = t_1.team_id
                           JOIN public.team t_2 ON game.team_2 = t_2.team_id''')
            return {f'{game[0].strftime('%m-%d-%Y')}.{game[1]}': game[2:] for game in cur.fetchall()}

    def select(self, cur, table, columns, check_columns, search_vals, custom_exception=''):
        '''
        Simple select from database

        Args:
            cur (con.cursor()): Cursor for database.
            table (str): Table being accessed.
            columns (list[str]): Columns being returned from table.
            check_columns (list[str]): List of columns being checked.
            search_vals (list[values]): Values being check for.
            custom_exception (str): Exception to be thrown if nothing is returned.
        '''
        columns_str = ','.join(columns)
        check_columns_str = '=%s AND '.join(check_columns) + '=%s'
        query_str = f'''SELECT {columns_str} FROM public.{table} WHERE {check_columns_str}'''
        cur.execute(query_str, search_vals)
        values = cur.fetchall()
        if custom_exception and not values:
            raise DB_Exception(custom_exception)
        return values

    def insert(self, cur, table, columns, values, custom_exception=''):
        '''
        Simple insert from database

        Args:
            cur (con.cursor()): Cursor for database.
            table (str): Table being accessed.
            columns (list[str]): Columns being given data.
            search_vals (list[values]): Data being given to columns.
            custom_exception (str): Exception to be thrown if exception is thrown.
        '''
        columns_str = ','.join(columns)
        values_str = ','.join(['%s' for _ in columns])
        query_str = f'''INSERT INTO public.{table} ({columns_str}) VALUES ({values_str})'''
        try:
            cur.execute(query_str, values)
        except Exception as e:
            print(e)
            if custom_exception:
                raise DB_Exception(custom_exception)
            raise e

    def update(self, cur, table, set_columns, set_values, condition_columns, check_values, custom_exception=''):
        '''
        Simple update from database

        Args:
            cur (con.cursor()): Cursor for database.
            table (str): Table being accessed.
            set_columns (list[str]): Columns being updated in table.
            set_values (list[str]): Update values for columns in table.
            condition_columns (list[str]): List of columns being checked.
            check_values (list[values]): Values being check for.
            custom_exception (str): Exception to be thrown if exception is thrown.
        '''
        set_str = '=%s,'.join(set_columns) + '=%s'
        condition_str = '=%s AND '.join(condition_columns) + '=%s'

        values = (*set_values, *check_values)

        query_str = f'''UPDATE public.{table} SET {set_str} WHERE {condition_str}'''
        try:
            cur.execute(query_str, values)
        except Exception as e:
            if custom_exception:
                raise DB_Exception(custom_exception)
            raise

    def delete(self, cur, table, condition_columns, values, custom_exception=''):
        condition_str = '=%s,'.join(condition_columns) + '=%s'
        query_str = f'''DELETE FROM public.{table} WHERE {condition_str}'''

        try:
            cur.execute(query_str, values)
        except Exception:
            if custom_exception:
                raise DB_Exception(custom_exception)
            raise

    def select_player_id(self, cur, username, custom_exception=''):
        return self.select(cur, 'player', ['player_id'],
                           ['username'], (username, ), custom_exception)[0][0]

    def select_username(self, cur, player_id, custom_exception=''):
        return self.select(cur, 'player', ['username'],
                           ['player_id'], (player_id, ), custom_exception)[0][0]

    def select_team(self, cur, team_name, custom_exception=''):
        return self.select(cur, 'team', ['team_id'], ['team_name'], 
                           (team_name,), custom_exception)[0][0]
    
    def select_2_teams(self, cur, team_1, team_2):
        return simple_sort(self.select_team(cur, team_1, 'Could not find team 1'),
                           self.select_team(cur, team_2, 'Could not find team 2'))

    def check_round_exists(self, cur, game_id, round_number):
        return bool(self.select(cur, 'round', ['round_number'], ['game_id', 'round_number'], (game_id, round_number)))

    def submit_team(self, data):
        '''
        Handle team being added

        Args:
            data (dict):
                'player1': First player of team
                'player2': Second player of team
                'updateTeam': Whether team should be updated or not
                'selectedTeam': Selected team to be updated
                'teamName': Name of team
        '''
        if data['player1'] == data['player2']:
            raise DB_Exception('A team must have two unique players')

        try:
            with self.con.cursor() as cur:
                # Get player IDs
                player_id_1 = self.select(cur, 'player', ['player_id'],
                                          ['username'], (data['player1'],),
                                          f'Player not found in database {data["player1"]}')[0][0]
                player_id_2 = self.select(cur, 'player', ['player_id'],
                                          ['username'], (data['player2'],),
                                          f'Player not found in database {data["player2"]}')[0][0]

                # Make sure player_id_1 is the lower number
                player_id_1, player_id_2 = simple_sort(player_id_1, player_id_2)

                if data['updateTeam']:
                    # Update existing team
                    if data['selectedTeam'] == None or data['selectedTeam'] == 'None':
                        raise DB_Exception(f'Update team was set to true but no team was selected. {data["selectedTeam"]=}')

                    # Find already added team
                    team_data = self.select(cur, 'team',
                                            ['team_id', 'team_name', 'player_1', 'player_2'],
                                            ['team_name'], (data['selectedTeam'],),
                                            f'Could not find team in database {data["selectedTeam"]}')[0]

                    # Set team data to variables
                    team_id = team_data[0]
                    previous_team_name = team_data[1]

                    # Order players
                    previous_player_id_1, previous_player_id_2 = simple_sort(team_data[2], team_data[3])

                    # Players cannot be changed
                    if previous_player_id_1 != player_id_1 or previous_player_id_2 != player_id_2:
                        raise DB_Exception('Only team name can be updated. New team must be create for different players.')

                    if previous_team_name == data['teamName']:
                        print('Team name is the same. No changes made.')
                    else:
                        self.update(cur, 'team', ['team_name'],
                                    (data['teamName'],), ['team_id'], (team_id,))

                else:
                    # Create new team
                    self.insert(cur, 'team', ['player_1', 'player_2', 'team_name'],
                                (player_id_1, player_id_2, data['teamName']))
        except Exception:
            self.con.rollback()
            raise
        self.con.commit()

    def delete_team(self, data):
        '''
        Delete Team. Only deletes teams with no connections

        Args:
            data (dict):
                'selectedTeam': Team to be deleted
        '''
        try:
            with self.con.cursor() as cur:
                team_id = self.select(cur, 'team', ['team_id'],  
                                      ['team_name'], (data['selectedTeam'],), 
                                      'Could not find selected team')[0]

                query_str = f'''SELECT game_id FROM public.game WHERE team_1=%s OR team_2=%s'''
                cur.execute(query_str, (team_id, team_id))
                if cur.fetchall():
                    raise DB_Exception(f'Cannot delete {data["selectedTeam"]} because it has connected data')

                self.delete(cur, 'team', ['team_id'], (team_id,), f'Could not delete team {data["selectedTeam"]}')

        except Exception:
            self.con.rollback()
            raise
        self.con.commit()

    def submit_player(self, data):
        '''
        Handle player being added

        Args:
            data (dict):
                'username': First player of team
                'first_name': Second player of team
                'updatePlayer': Whether player should be updated or not
                'selectedPlayer': Selected player to be updated
        '''
        try:
            with self.con.cursor() as cur:
                if data['updatePlayer']:
                    # Update player
                    if (data['selectedPlayer'] == data['username']):
                        print('Username was the same')
                        return

                    # Get players id
                    player_id = self.select(cur, 'player', ['player_id'],
                                            ['username'], (data['selectedPlayer'], ),
                                            f'Could not find player to update {data["selectedPlayer"]}')[0][0]

                    # Update player with new data
                    self.update(cur, 'player', ['username', 'first_name'],
                                (data['username'], data['firstName']), ['player_id'],
                                (player_id, ), f'Could not update {data["selectedPlayer"]}')
                else:
                    # Create new player
                    self.insert(cur, 'player', ['username', 'first_name'],
                                (data['username'], data['firstName']),
                                f'Could not add player with username {data["username"]}')
        
        except Exception:
            self.con.rollback()
            raise
        self.con.commit()

    def delete_player(self, data):
        '''
        Delete Player. Only deletes players with no connections

        Args:
            data (dict):
                'selectedPlayer': Player to be deleted
        '''
        try:
            with self.con.cursor() as cur:
                player_id = self.select(cur, 'player', ['player_id'],  
                                      ['username'], (data['selectedPlayer'],), 
                                      'Could not find selected player')[0]

                query_str = f'''SELECT team_id FROM public.team WHERE player_1=%s OR player_2=%s'''
                cur.execute(query_str, (player_id, player_id))

                if cur.fetchall():
                    raise DB_Exception(f'Cannot delete {data["selectedPlayer"]} because it has connected data')
                self.delete(cur, 'player', ['player_id'], (player_id,), f'Could not delete player {data["selectedPlayer"]}')

        except Exception:
            self.con.rollback()
            raise
        self.con.commit()
    
    def create_pinochle_match(self, data):
        '''
        Add Game

        Args:
            data(dict):
                'date': Day game was played.
                'gameOfDay': Game number of the day.
                'team1': team name of team one
                'team2': team name of team two
        '''
        try:
            with self.con.cursor() as cur:
                team_1_id = self.select(cur, 'team', ['team_id'],  
                                      ['team_name'], (data['team1'],), 
                                      'Could not find Team 1')[0][0]

                team_2_id = self.select(cur, 'team', ['team_id'],  
                                      ['team_name'], (data['team2'],), 
                                      'Could not find Team 2')[0][0]
                print(team_1_id)
                print(team_2_id)
                team_1_id, team_2_id = simple_sort(team_1_id, team_2_id)

                game = self.select(cur, 'game', ['game_id'], ['team_1', 'team_2', 'game_date', 'game_of_day'],
                                   (team_1_id, team_2_id, data['date'], data['gameOfDay']))
                if game:
                    raise DB_Exception('Game already exists')
                
                self.insert(cur, 'game', ['team_1', 'team_2', 'game_date', 'game_of_day'],
                            (team_1_id, team_2_id, data['date'], data['gameOfDay']),
                            'Could not create game')

        except Exception:
            self.con.rollback()
            raise
        self.con.commit()

    def get_pinochle_match_by_teams(self, data):
        '''
        Load matches between two teams

        Args:
            data(dict):
                'team1': team name of team one
                'team2': team name of team two

        '''
        with self.con.cursor() as cur:
            team_1_id, team_2_id = self.select_2_teams(cur, data['team1'], data['team2'])
            print(team_1_id, team_2_id)
            games = self.select(cur, 'game', ['game_date', 'game_of_day'],
                                ['team_1', 'team_2'], (team_1_id, team_2_id))
            return [f'{game[0].strftime('%m-%d-%Y')}.{game[1]}' for game in games]

    def load_pinochle_match(self, data):
        '''
        Args:
            data(dict):
                'date': Day game was played.
                'gameOfDay': Game number of the day.
                'team1': team name of team one
                'team2': team name of team two
        '''
        with self.con.cursor() as cur:
            team_1_id, team_2_id = self.select_2_teams(cur, data['team1'], data['team2'])
            game_id = self.select(cur, 'game', ['game_id'],
                               ['team_1', 'team_2', 'game_date', 'game_of_day'],
                               (team_1_id, team_2_id, data['date'], data['gameOfDay']),
                               'Could not find game')[0][0]
            print(game_id)

            rounds = self.select(cur, 'round', ['round_number', 'trump', 'bid', 'top_bidder', 'meld_1', 'meld_2', 'tricks_1', 'tricks_2'],
                                 ['game_id'], (game_id,))
            print(rounds)
            return [{'trump': round[1], 'bid': round[2], 'top_bidder': self.select_username(cur, round[3]), 'meld_1': round[4], 'meld_2': round[5], 'tricks_1': round[6], 'tricks_2': round[7]} for round in rounds]

    def submit_round(self, data):
        '''
        Add round to database

        Args:
            data (dict):
                'game_id':
                'round_number':
                'trump':
                'bid':
                'top_bidder':
                'meld_1':
                'meld_2':
                'tricks_1':
                'tricks_2':
        '''
        try:
            with self.con.cursor() as cur:
                top_bidder_id = self.select_player_id(cur, data['top_bidder'], 'Could not find top bidder')
                if self.check_round_exists(cur, data['game_id'], data['round_number']):
                    self.update(cur, 'round', ['trump', 'bid', 'top_bidder', 'meld_1', 'meld_2', 'tricks_1', 'tricks_2'],
                                (data['trump'], data['bid'], top_bidder_id, data['meld_1'], data['meld_2'], data['tricks_1'], data['tricks_2']),
                                ['game_id', 'round_number'], (data['game_id'], data['round_number']),
                                'Failed to update round')
                else:

                    self.insert(cur, 'round',
                                ['game_id', 'round_number', 'trump', 'bid', 'top_bidder', 'meld_1', 'meld_2', 'tricks_1', 'tricks_2'],
                                (data['game_id'], data['round_number'], data['trump'], data['bid'], top_bidder_id,
                                data['meld_1'], data['meld_2'], data['tricks_1'], data['tricks_2']),
                                'Failed to add round')
        
        except Exception:
            self.con.rollback()
            raise
        self.con.commit()
