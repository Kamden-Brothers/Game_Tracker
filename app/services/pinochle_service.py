from app.classes.game.Pinochle import Pinochle
from app.classes.game.gateway.PinochleGateway import PinochleGateway
from app.services.player_service import PlayerService
from app.services.team_service import TeamService

class PinochleService:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @staticmethod
    def get_class(conn):
        player = PlayerService.get_class(conn)
        team = TeamService.get_class(conn)
        return Pinochle(PinochleGateway(conn), player, team)
    
    @staticmethod
    def check_keys(data: dict, keys: list):
        for key in keys:
            if key not in data.keys():
                raise Exception(f'Missing required key {key}')
    
    @staticmethod
    def check_general_keys(data: dict):
        PinochleService.check_keys(data, ['team1', 'team2', 'date', 'gameOfDay'])

    def get_games_for_matchup(self, data) -> dict:
        with self.db_pool.connection() as conn:
            self.check_keys(data, ['team1', 'team2'])
            team_name_1 = data['team1']
            team_name_2 = data['team2']
            return self.get_class(conn).get_games_for_matchup(team_name_1, team_name_2)

    def create_game(self, data: dict) -> dict:
        with self.db_pool.connection() as conn:
            self.check_general_keys(data)
            return self.get_class(conn).create_game(data['team1'], data['team2'], data['date'], data['gameOfDay'])
    
    def load_game(self, data: dict) -> dict:
        with self.db_pool.connection() as conn:
            self.check_general_keys(data)
            return self.get_class(conn).load_game(data['team1'], data['team2'], data['date'], data['gameOfDay'])

    def delete_game(self, data: dict) -> dict:
        with self.db_pool.connection() as conn:
            self.check_general_keys(data)
            return self.get_class(conn).delete_game(data['team1'], data['team2'], data['date'], data['gameOfDay'])

    def submit_round(self, data: dict) -> dict:
        with self.db_pool.connection() as conn:
            pinochle = self.get_class(conn)

    def delete_round(self, data: dict) -> dict:
        with self.db_pool.connection() as conn:
            pinochle = self.get_class(conn)
