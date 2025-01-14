import webbrowser
import logging

from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS

from DataBase.DBCommands import DBWorker

db_worker = DBWorker()

# data = {'game_id': 9,
#         'round_number': 3,
#         'trump': 'Spades',
#         'bid': 51,
#         'top_bidder': 'BooksRBetter',
#         'meld_1': '60',
#         'meld_2': '20',
#         'tricks_1': '35',
#         'tricks_2': '15'
# }
# db_worker.submit_round(data)

# print(db_worker.load_pinochle_match({'team1': 'Kamilya', 'team2': 'The Inlaws', 'date': '2025-01-03', 'gameOfDay': '1'}))
# exit()

players = db_worker.get_players()
teams = db_worker.get_teams()
pinochle_matches = db_worker.get_pinochle_matches()

print(players)
print(teams)
print(pinochle_matches)

# Set path for log
logging.basicConfig(filename='record.log', level=logging.DEBUG)

# Create app instance
app = Flask(__name__, template_folder='vue/dist', static_folder='vue/dist/assets')
CORS(app)


@app.route('/current_teams')
def current_teams():
    return teams


@app.route('/current_players')
def current_players():
    print('Called player data')
    return players


@app.route('/submit_team', methods=['POST'])
def submit_team():
    print('submit_team')
    try:
        data = request.get_json()
        db_worker.submit_team(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

    # Update list of teams
    global teams
    teams = db_worker.get_teams()
    return {'status': 'success', 'data': None}


@app.route('/delete_team', methods=['POST'])
def delete_team():
    print('delete_team')
    try:
        data = request.get_json()
        db_worker.delete_team(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

    # Update list of teams
    global teams
    teams = db_worker.get_teams()
    print(teams)
    return {'status': 'success', 'data': None}


@app.route('/submit_player', methods=['POST'])
def submit_player():
    print('submit_player')
    try:
        data = request.get_json()
        db_worker.submit_player(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

    # Update list of teams
    global players
    players = db_worker.get_players()
    print(players)
    return {'status': 'success', 'data': None}

   
@app.route('/delete_player', methods=['POST'])
def delete_player():
    print('delete_player')
    try:
        data = request.get_json()
        db_worker.delete_player(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

    # Update list of teams
    global players
    players = db_worker.get_players()
    print(players)
    return {'status': 'success', 'data': None}


@app.route('/create_pinochle_match', methods=['POST'])
def create_pinochle_match():
    print('create pinochle match')
    try:
        data = request.get_json()
        print(data)
        db_worker.create_pinochle_match(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

    return {'status': 'success', 'data': None}


@app.route('/load_pinochle_match', methods=['POST'])
def load_pinochle_match():
    try:
        data = request.get_json()
        print(data)
        matchup_matches = db_worker.load_pinochle_match(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}
    
    return {'status': 'success', 'data': matchup_matches}


@app.route('/pinochle_matches', methods=['POST'])
def pinochle_matches():
    try:
        data = request.get_json()
        matchup_matches = db_worker.get_pinochle_match_by_teams(data)
    except Exception as e:
        print(e)
        return {'status': 'error', 'message': str(e)}

    
    return {'status': 'success', 'data': matchup_matches}


@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    # Let Vue handle the routing
    return send_from_directory(app.template_folder, 'index.html')


if __name__=='__main__':
    webbrowser.open('http://127.0.0.1:5000/create_game')
    app.run()