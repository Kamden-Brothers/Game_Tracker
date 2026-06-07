from psycopg2.extensions import connection

from .gateway.TeamGateway import TeamGateway
from app.classes.player.Player import Player

class Team:
    def __init__(self, db: connection, player: Player):
        self.gateway = TeamGateway(db)
        self.player = player
    
    @staticmethod
    def simple_sort(first, second):
        '''
        Places lowest item in first position
        '''
        if first > second:
            return second, first
        return first, second

    def get_all_teams(self):
        return self.gateway.get_all_teams()

    def submit_team(self, data):
        '''
        Handle team being added

        Args:
            data (dict):
                'player1': First player of team
                'player2': Second player of team
                'updateTeam': Whether team should be updated or not
                'teamName': Name of team
        '''
        player1 = data['player1']
        player2 = data['player2']
        should_update_team = data['updateTeam']
        team_name = data['teamName']

        if not player1:
            raise Exception('Player one is required')
        if not player2:
            raise Exception('Player two is required')
        if not team_name:
            raise Exception('Team name is required')

        if data['player1'] == data['player2']:
            raise Exception('A team must have two unique players')
        
        player_id_1 = self.player.get_player_id(data['player1'])
        player_id_2 = self.player.get_player_id(data['player2'])

        if (not player_id_1 or not player_id_2):
            raise Exception('Could not find a player')

        # Make sure player_id_1 is the lower number
        player_id_1, player_id_2 = self.simple_sort(player_id_1, player_id_2)

        if should_update_team:
            if not self.gateway.update_team(team_name, player_id_1, player_id_2):
                raise Exception('No teams were updated')

        else:
            self.gateway.insert_team(team_name, player_id_1, player_id_2)

    def delete_team(self, data):
        selected_team = data['selectedTeam']
        if (not selected_team):
            raise Exception('Selected team is required to delete')

        if not self.gateway.delete_team(selected_team):
            return {'status': False, 'error': 'Failed to delete team'}
        return {'status': True}
