from .gateway.PinochleGateway import PinochleGateway
from app.classes.team.Team import Team
from app.classes.player.Player import Player


class Pinochle:
    def __init__(self, gateway: PinochleGateway, player: Player, team: Team):
        self.gateway = gateway
        self.player = player
        self.team = team

    @staticmethod
    def verify_team_names(team_name_1: str, team_name_2: str):
        if (not team_name_1 or not team_name_2):
            raise Exception(f'Missing one or both team names')

        if (team_name_1 == team_name_2):
            raise Exception(f'Cannot be the same team name')
    
    def get_teams_in_order(self, team_name_1, team_name_2):
        self.verify_team_names(team_name_1, team_name_2)
        return self.team.get_teams_in_order(team_name_1, team_name_2)
    
    def get_games_for_matchup(self, team_name_1: str, team_name_2: str) -> dict:
        self.verify_team_names(team_name_1, team_name_2)
        team_info_1, team_info_2 = self.team.get_teams_info_in_order(team_name_1, team_name_2)
        matches = self.gateway.get_games_for_matchup(team_info_1['team_id'], team_info_2['team_id'])
        data = {
                'matches': matches,
                'team1': team_info_1,
                'team2': team_info_2
            }
        return {'status': True, 'data': data}

    def create_game(self, team_name_1: str, team_name_2: str, game_date: str, game_of_day: int):
        team_id_1, team_id_2 = self.get_teams_in_order(team_name_1, team_name_2)
        latest_game_num = self.gateway.get_next_match_number(team_id_1, team_id_2)
        if latest_game_num != game_of_day:
            return {'status': False, 'error': f'Match number expected to be {latest_game_num}'}

        if not self.gateway.create_game(team_id_1, team_id_2, game_date, latest_game_num):
            return {'status': False, 'error': 'Failed to create game'}
        return {'status': True}

    def load_game(self, team_name_1: str, team_name_2: str, game_date: str, game_of_day: int):
        team_id_1, team_id_2 = self.get_teams_in_order(team_name_1, team_name_2)
        game_id = self.gateway.get_game_id(team_id_1, team_id_2, game_date, game_of_day)
        if game_id is None:
            return {'status': False, 'error': 'Game not found'}
        return {'status': True, 'data': {'rounds': self.gateway.load_game(game_id)}}

    def delete_game(self, team_name_1: str, team_name_2: str, game_date: str, game_of_day: int):
        team_id_1, team_id_2 = self.get_teams_in_order(team_name_1, team_name_2)
        if not self.gateway.delete_game(team_id_1, team_id_2, game_date, game_of_day):
            return {'status': False, 'error': 'Game was not able to be deleted'}
        return {'status': True}

