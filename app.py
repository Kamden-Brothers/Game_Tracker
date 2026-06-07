import webbrowser
import logging
import traceback

from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS

from app.DBCommands import DBWorker
from app.services.player_service import PlayerService
from app.services.team_service import TeamService
from app.ConnectToDB import db_pool

db_worker = DBWorker()

player_services = PlayerService(db_pool)
team_services = TeamService(db_pool)
pinochle_matches = db_worker.get_pinochle_matches()


# Set path for log
logging.basicConfig(filename='record.log', level=logging.DEBUG)

# Create app instance
app = Flask(__name__, template_folder='vue/dist', static_folder='vue/dist/assets')
CORS(app)

@app.route('/current_players')
def current_players():
    return player_services.get_all_players()

@app.route('/submit_player', methods=['POST'])
def submit_player():
    print('submit_player')
    try:
        data = request.get_json()
        return player_services.submit_player(data)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return {'status': 'error', 'message': 'Database error occurred'}

   
@app.route('/delete_player', methods=['POST'])
def delete_player():
    print('delete_player')
    try:
        data = request.get_json()
        return player_services.delete_player(data)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return {'status': 'error', 'message': str(e)}


@app.route('/current_teams')
def current_teams():
    return team_services.get_all_teams()

@app.route('/submit_team', methods=['POST'])
def submit_team():
    print('submit_team')
    try:
        data = request.get_json()
        team_services.submit_team(data)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return {'status': 'error', 'message': str(e)}

    return {'status': 'success', 'data': None}

@app.route('/delete_team', methods=['POST'])
def delete_team():
    print('delete_team')
    try:
        data = request.get_json()
        team_services.delete_team(data)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return {'status': 'error', 'message': str(e)}

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
        print(traceback.format_exc())
        return {'status': 'error', 'message': str(e)}

    return {'status': 'success', 'data': None}


@app.route('/submit_pinochle_game', methods=['POST'])
def submit_pinochle_game():
    try:
        data = request.get_json()
        print(data)
        db_worker.submit_pinochle_game(data)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
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
        print(traceback.format_exc())
        return {'status': 'error', 'message': str(e)}
    
    return {'status': 'success', 'data': matchup_matches}


@app.route('/pinochle_matches', methods=['POST'])
def pinochle_matches():
    try:
        data = request.get_json()
        matchup_matches = db_worker.get_pinochle_match_by_teams(data)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
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