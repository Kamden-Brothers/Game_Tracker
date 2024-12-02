import tkinter as tk
import time
import os

from data_base import DB
from calc_stats import calc_stats

data_base = DB()


def find_user(user_id):
    query_text = 'SELECT "P_ID", "Player_Name" FROM public."Player" WHERE "P_ID"=%s'
    record = (user_id, )
    game_info = data_base.execute(query_text, record)
    return [game_info[0], game_info[1]]
    

def find_team(team_id):
    query_text = 'SELECT "T_ID", "Player_1", "Player_2", "Friendly_Name" FROM public."Team" WHERE "T_ID" = %s'
    record = (team_id, )
    game_info = data_base.execute(query_text, record)
    
    player_1 = game_info[1]
    player_2 = game_info[2]
    team_name = game_info[3]

    return find_user(player_1), find_user(player_2), team_name
    

def find_game(game_id):
    query_text = 'SELECT "G_ID", "Team_1", "Team_2", "Date", "Game_Of_Day" FROM public."Game" WHERE "G_ID"=%s'
    record = (game_id, )
    game_info = data_base.execute(query_text, record)
    
    team_1 = game_info[1]
    team_2 = game_info[2]
    
    player_1, player_2, team_name_1 = find_team(team_1)
    player_3, player_4, team_name_2 = find_team(team_2)
    
    team_1_players = [player_1, player_2]
    team_2_players = [player_3, player_4]
    teams = [[team_1, team_name_1], [team_2, team_name_2]]
    game_details = [game_info[3], game_info[4]]
    return team_1_players, team_2_players, teams, game_details


def highest_round(game_id):
    query_text = f'SELECT "Round_Number" FROM public."Round" WHERE "Round_Number" = (SELECT MAX("Round_Number") FROM public."Round" WHERE "Game_Number" = %s) AND "Game_Number" = %s'
    record = (game_id, game_id)
    top_num = data_base.execute(query_text, record)
    
    if top_num:
        return top_num[0]
    return 0

def enter_record(game_id):
    os.system('cls')

    round_number = highest_round(game_id) + 1
    print(round_number)
    if round_number == 1:
        current_total_1 = 0
        current_total_2 = 0

    else:
        query_text = f'SELECT SUM("Points_Gain_1"), SUM("Points_Gain_2") FROM public."Round" WHERE "Game_Number"={game_id}'
        record = ()
        current_total_1, current_total_2 = data_base.execute(query_text, record)

    print()
    print(f'Current round number = {round_number}')
    print(f'Current Team 1 points = {current_total_1}')
    print(f'Current Team 2 points = {current_total_2}')
    print()
    
    team_1_players, team_2_players, teams, game_details = find_game(game_id)
    # print(team_1_players, team_2_players, teams)
    
    def get_int(message):
        print()
        while True:
            user_input = input(message + '\n')
            if user_input.isdigit():
                return int(user_input)
    
    def get_suit():
        print()
        message = 'Trump suit\n'
        suits = ['spades', 'clubs', 'diamonds', 'hearts']
        valid_numbers = [0, 1, 2, 3]
        for i, suit in enumerate(suits):
            message += f'{i}: {suit}\n'
        
        while True:
            user_input = input(message)
            if user_input.isdigit():
                if int(user_input) in valid_numbers:
                    return suits[int(user_input)]

    def top_bid():
        valid_numbers = [0]
        message = '\nENTER TOP BIDDER NUMBER\n'
        for player in team_1_players + team_2_players:
            message += f'{player[0]}: {player[1]}\n'
            valid_numbers.append(player[0])
        message += '0: UNKNOWN\n' 

        while True:
            user_input = input(message)
            if user_input.isdigit():
                if int(user_input) in valid_numbers:
                    return int(user_input)
                else:
                    print('NOT A VALID NUMBER\n')
                    time.sleep(2)
    
    def team_took_bid(top_bidder):
        if top_bidder in [p[0] for p in team_1_players]:
            return teams[0][0]
        if top_bidder in [p[0] for p in team_2_players]:
            return teams[1][0]

        valid_numbers = []
        message = 'Which team took bid\n'
        for team in teams:
            message += f'{team[0]}: {team[1]}\n'
            valid_numbers.append(team[0])

        while True:
            user_input = input(message)
            if user_input.isdigit():
                if int(user_input) in valid_numbers:
                    return int(user_input)
                else:
                    print('NOT A VALID NUMBER\n')
                    time.sleep(.5)
    
    def calc_points(meld, tricks, took_bid, bid_number, other_tricks):
        if tricks + other_tricks == 0:
            if took_bid:
                return bid_number * -1
            return meld
        
        elif tricks + other_tricks != 50:
            raise Exception(f'Tricks do not add up to 50 {tricks} + {other_tricks}')
        
        if meld < 20:
            meld = 0

        if tricks < 20:
            meld = 0
            tricks = 0
        
        points_gained = meld + tricks
        if took_bid:
            if points_gained < bid_number:
                return bid_number * -1

        return points_gained

    bid = get_int('Bid')
    trump = get_suit()
    top_bidder = top_bid()

    team_bid = team_took_bid(top_bidder)
    meld_1 = get_int('Team 1 meld')
    meld_2 = get_int('Team 2 meld')
    tricks_1 = get_int('Team 1 tricks')
    tricks_2 = get_int('Team 2 tricks')
    
    points_gain_1 = calc_points(meld_1, tricks_1, team_bid == teams[0][0], bid, tricks_2)
    points_gain_2 = calc_points(meld_2, tricks_2, team_bid ==  teams[1][0], bid, tricks_1)
    
    new_total_1 = current_total_1 + points_gain_1
    new_total_2 = current_total_2 + points_gain_2
    
    query_text = '''INSERT INTO public."Round"("Round_Number", "Bid", "Game_Number", "Trump", "Top_Bidder",
                     "Meld_1", "Meld_2", "Tricks_1", "Tricks_2", "Points_Gain_1", "Points_Gain_2", "Current_Total_1", "Current_Total_2", "Team_Bid")
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    
    record = (round_number, bid, game_id, trump, top_bidder,
              meld_1, meld_2, tricks_1, tricks_2, points_gain_1, points_gain_2,
              new_total_1, new_total_2, team_bid)
    print(record)
    print(f'{round_number=}')
    print(f'{bid=}')
    print(f'{game_id=}')
    print(f'{trump=}')
    print(f'{top_bidder=}')
    print(f'{team_bid=}')
    print(f'{meld_1=}')
    print(f'{meld_2=}')
    print(f'{tricks_1=}')
    print(f'{tricks_2=}')
    print(f'{points_gain_1=}')
    print(f'{points_gain_2=}')
    print(f'{new_total_1=}')
    print(f'{new_total_2=}')
    print()
    print()
    
    skip = input('Hit Enter to continue Or send SKIP to abort\n')
    if 'skip' == skip.lower():
        return
    game_info = data_base.execute(query_text, record, commit=True)
    
    if new_total_1 >= 500 and new_total_1 >= new_total_2:
        if team_bid == teams[0][0]:
            print('Team one Won')
            return True
    
    if new_total_2 >= 500 and new_total_2 >= new_total_1:
        if team_bid == teams[1][0]:
            print('Team two Won')
            return True

def add_game_data():
    game_id = int(input('Enter game number\n'))
    team_1_players, team_2_players, teams, game_details = find_game(game_id)
    input(f'\nEntering results for game {game_details[0]} played on {game_details[1]}\nBetween team {teams[0][1]} and {teams[1][1]}\n')
    while True:
        if enter_record(game_id):
            break

# add_game_data()
calc_stats(data_base)
