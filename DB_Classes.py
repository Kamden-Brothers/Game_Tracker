'''
Classes used in database
'''

class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        
    def __repr__(self):
        return f"Player({self.player_id}, {self.name})"


class Team:
    def __init__(self, team_id, player_1, player_2, team_name):
        self.team_id = team_id
        self.player_1 = player_1
        self.player_2 = player_2
        self.team_name = team_name


class Game:
    def __init__(self, game_id, team_1, team_2, date, game_of_day):
        self.game_id = game_id
        self.team_1 = team_1
        self.team_2 = team_2
        self.date = date
        self.game_of_day = game_of_day

    def add_round(self, round_obj):
        # Logic to add round to the game
        pass


class Suit:
    def __init__(self, suit):
        self.suit = suit

class Round:
    def __init__(self, round_number, bid, trump, top_bidder, meld_1, meld_2, tricks_1, tricks_2):
        # Composite key (round_number, game_id)
        self.round_number = round_number
        self.game_id
        self.bid = bid
        self.trump = trump
        self.top_bidder = top_bidder
        self.meld_1 = meld_1
        self.meld_2 = meld_2
        self.tricks_1 = tricks_1
        self.tricks_2 = tricks_2
        self.points_gain_1 = 0
        self.points_gain_2 = 0

    def calculate_points(self):
        # Calculate points based on meld and tricks
        pass
