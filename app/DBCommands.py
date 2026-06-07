from app import ConnectToDB


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

        print('running select')
        print(query_str)
        print(search_vals)
        print()
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

    def select_team_name(self, cur, team_id, custom_exception=''):
        return self.select(cur, 'team', ['team_name'],
                           ['team_id'], (team_id, ), custom_exception)[0][0]

    def select_team_id(self, cur, team_name, custom_exception=''):
        return self.select(cur, 'team', ['team_id'], ['team_name'], 
                           (team_name,), custom_exception)[0][0]
    
    def select_2_teams(self, cur, team_1, team_2):
        return simple_sort(self.select_team_id(cur, team_1, 'Could not find team 1'),
                           self.select_team_id(cur, team_2, 'Could not find team 2'))

    def select_team_players(self, cur, team_id):
        player_1, player_2, team_name = self.select(cur, 'team', ['player_1', 'player_2', 'team_name'], ['team_id'],
                                                    (team_id,), f'Could not find team with id {team_id}')[0]
        return {
            'team_name': team_name,
            'player_1': self.select_username(cur, player_1, f'Could not find player one {player_1} on team {team_id}'),
            'player_2': self.select_username(cur, player_2, f'Could not find player one {player_2} on team {team_id}')
        }

    def select_game(self, cur, team_1, team_2, game_date, game_of_day):
        team_1_id, team_2_id = self.select_2_teams(cur, team_1, team_2)
        return self.select(cur, 'game', ['game_id'],
                           ['team_1', 'team_2', 'game_date', 'game_of_day'],
                           (team_1_id, team_2_id, game_date, game_of_day),
                           f'Could not find game {game_date=} {game_of_day=} {team_1=} {team_2=}')[0][0]

    def check_round_exists(self, cur, game_id, round_number):
        return bool(self.select(cur, 'round', ['round_number'], ['game_id', 'round_number'], (game_id, round_number)))

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
            team_1_info = self.select_team_players(cur, team_1_id)
            team_2_info = self.select_team_players(cur, team_2_id)

            games = self.select(cur, 'game', ['game_date', 'game_of_day'],
                                ['team_1', 'team_2'], (team_1_id, team_2_id))
            return {
                'matches': [f'{game[0].strftime('%m-%d-%Y')}.{game[1]}' for game in games],
                'team1': team_1_info,
                'team2': team_2_info
            }

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
            game_id = self.select_game(cur, data['team1'], data['team2'], data['date'], data['gameOfDay'])
            print(game_id)

            rounds = self.select(cur, 'round', ['round_number', 'trump', 'bid', 'top_bidder', 'meld_1', 'meld_2', 'tricks_1', 'tricks_2'],
                                 ['game_id'], (game_id,))
            return {
                'rounds': [{'round_number': round[0], 'trump': round[1], 'bid': round[2], 'top_bidder': self.select_username(cur, round[3]), 'meld_1': round[4], 'meld_2': round[5], 'tricks_1': round[6], 'tricks_2': round[7]} for round in rounds]
                }

    def submit_round(self, cur, data, game_id, team_bid_number):
        if not isinstance(data['meld_1'], int) and isinstance(data['meld_2'], int) and isinstance(data['tricks_1'], int) and isinstance(data['tricks_2'], int):
            raise DB_Exception('Meld, tricks, and bid must be an integer')

        if (data['meld_1'] > 0 and data['meld_1'] < 20 or data['meld_2'] > 0 and data['meld_2'] < 20):
            raise DB_Exception('Meld cannot be between 0 and 20')

        if (data['tricks_1'] + data['tricks_2'] != 0 and data['tricks_1'] + data['tricks_2'] != 50):
            raise DB_Exception('Tricks must be 0 or 50')
        
        if (data['tricks_1'] + data['tricks_2'] == 0):
            if data[f'meld_{team_bid_number}'] != 0:
                raise DB_Exception('Bidder cannot have no meld if tricks are 0')

        if (data['bid'] < 50 or (data['bid'] > 60 and data['bid'] % 5 != 0)):
            raise DB_Exception('Bid must be 50-60 or a divisible of 5 above 60')

        top_bidder_id = self.select_player_id(cur, data['top_bidder'], 'Could not find top bidder')
        if self.check_round_exists(cur, game_id, data['round_number']):
            self.update(cur, 'round', ['trump', 'bid', 'top_bidder', 'meld_1', 'meld_2', 'tricks_1', 'tricks_2'],
                        (data['trump'], data['bid'], top_bidder_id, data['meld_1'], data['meld_2'], data['tricks_1'], data['tricks_2']),
                        ['game_id', 'round_number'], (game_id, data['round_number']),
                        'Failed to update round')
        else:
            self.insert(cur, 'round',
                        ['game_id', 'round_number', 'trump', 'bid', 'top_bidder', 'meld_1', 'meld_2', 'tricks_1', 'tricks_2'],
                        (game_id, data['round_number'], data['trump'], data['bid'], top_bidder_id,
                        data['meld_1'], data['meld_2'], data['tricks_1'], data['tricks_2']),
                        'Failed to add round')

    def submit_pinochle_game(self, data):
        try:
            with self.con.cursor() as cur:
                game_id = self.select_game(cur, data['team1'], data['team2'], data['date'], data['gameOfDay'])
                team_1_id, team_2_id = self.select_2_teams(cur, data['team1'], data['team2'])
                team_1_info = self.select_team_players(cur, team_1_id)
                team_2_info = self.select_team_players(cur, team_2_id)

                for num, round in enumerate(data['rounds']):
                    if round['top_bidder'] == team_1_info['player_1'] or round['top_bidder'] == team_1_info['player_2']:
                        team_bid_number = '1'
                    elif round['top_bidder'] == team_2_info['player_1'] or round['top_bidder'] == team_2_info['player_2']:
                        team_bid_number = '2'
                    else:
                        raise DB_Exception('Top bidder was not on either team')

                    round['round_number'] = num + 1
                    self.submit_round(cur, round, game_id, team_bid_number)

        except Exception as e:
            print(e)
            self.con.rollback()
            raise
        self.con.commit()
