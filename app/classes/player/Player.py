from .gateway.PlayerGateway import PlayerGateway

class Player:
    def __init__(self, gateway: PlayerGateway):
        self.gateway = gateway

    def get_all_players(self):
        return self.gateway.get_all_players()
    
    def get_player_id(self, username):
        if not username:
            raise Exception('username cannot be empty')
        return self.gateway.get_player_id(username)

    def submit_player(self, data):
        '''
        Handle player being added

        Args:
            data (dict):
                'username': First player of team
                'firstName': Second player of team
                'updatePlayer': Whether player should be updated or not
                'selectedPlayer': Selected player to be updated
        '''
        response = {'status': False}

        print(data)
        username = data['username']
        first_name = data['firstName']
        
        update_player = data['updatePlayer']
        selected_player = data['selectedPlayer']

        if (not username):
            response['error'] = 'Username cannot be empty'
            return response

        if (not first_name):
            response['error'] = 'Username cannot be empty'
            return response

        if (not selected_player and update_player):
            response['error'] = 'Selected player cannot be empty if updating a player'
            return response

        if (not update_player and selected_player):
            response['error'] = 'Selected player must be empty if not updating a player'
            return response
        
        if update_player:
            print('update')
            if not self.gateway.update_player(username, first_name, selected_player):
                response['error'] = 'Failed to update user'
                return response
        else:
            print('insert')
            self.gateway.insert_player(username, first_name)
        
        return {'status': True}

    def delete_player(self, data):
        username = data['selectedPlayer']
        if (not username):
            return {'status': False, 'error': 'Username is required to delete'}
        if not self.gateway.delete_player(username):
            return {'status': False, 'error': 'Failed to delete user'}
        return {'status': True}
