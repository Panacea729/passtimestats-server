from myorm import *
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/game/<game_id>', methods=['GET'])
def get_player_game_stats_endpoint(game_id):
    #game_id = request.args.get('game_id', type=int)
    steam_id = request.args.get('steam_id', type=int)

    game = Game.get_game(game_id)

    return jsonify(game.serialize(), status=200)

@app.route('/game/<game_id>/player_stats', methods=['GET'])
def get_player_game_stats_endpoint(game_id):
    steam_id = request.args.get('steam_id', type=int)

    game = Game.get_game(game_id)
    # A player could be on both teams
    blu_stats = PlayerTeamStats.get_player_team_stats(steam_id, game.blu_team.id)
    red_stats = PlayerTeamStats.get_player_team_stats(steam_id, game.red_team.id)

    return jsonify((blu_stats+red_stats).serialize())

@app.route('/game/<game_id>/team', methods=['GET'])
def get_player_game_stats_endpoint(game_id):
    team = request.args.get('team', type=str)

    game = Game.get_game(game_id)
    # A player could be on both teams
    team = game.blu_team if team.upper() == "RED" else game.red_team

    # gets the team data and stats of each player
    return jsonify(team.serialize())

@app.route('/get_player_aggregate_stats', methods=['GET'])
def get_player_aggregate_stats_endpoint():
    steam_id = request.args.get('steam_id', type=int)

    aggregate_stats = PlayerStats.get_player_total_stats(steam_id)

    return jsonify(aggregate_stats.serialize(), status=200)

@app.route('/game/create', methods=['GET'])
def get_player_aggregate_stats_endpoint():
    steam_id = request.args.get('steam_id', type=int)

    game = Game.parse_and_store_game()

    # TODO
    return jsonify("", status=200)

if __name__ == '__main__':
    app.run(debug=True)