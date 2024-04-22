from enum import Enum

import sqlite3
import json

# Load configuration from config.json (or defaultconfig.json if config.json doesn't exist)
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except Exception:
    with open('defaultconfig.json') as config_file:
        config = json.load(config_file)

# Use the database path from the configuration
DATABASE = config['database_path']

def get_db_connection():
    return sqlite3.connect(DATABASE)


class GameNotFoundError(Exception):
    '''
    Raised when game doesn't exist
    '''

class TeamNotFoundError(Exception):
    '''
    Raised when team doesn't exist
    '''

class PlayersNotFoundError(Exception):
    '''
    Raised when no players exist on a team
    '''

class AliasNotFoundError(Exception):
    '''
    Raised when no alias exists for a player
    '''


class TooManyRowsResult(Exception):
    '''
    thrown when result has too many rows
    '''

class GameResultNotFoundError(ValueError):
    '''
    Raised when the GameResult could not be parsed.
    '''

class GameResult(str, Enum):
    BLU_VICTORY = "BLU_VICTORY"
    RED_VICTORY = "RED_VICTORY"
    DRAW = "DRAW"

    @classmethod
    def parse(cls, string: str):
        try:
            return GameResult(string)
        except Exception:
            pass

        if string.upper() == "RED":
            return cls.RED_VICTORY
        if string.upper() == "BLU":
            return cls.BLU_VICTORY
        if string.upper() == "DRAW":
            return cls.DRAW
        
        raise GameResultNotFoundError

class PlayerStats():
    '''
    Stats of a player over multiple games
    '''
    def __init__(self, scores=0, steals=0, stolen_from=0, team_passes_thrown=0, team_passes_received=0,
                 intercepts_thrown=0, intercepts_received=0, blocks_thrown=0, blocks_received=0, assists_thrown=0, assists_received=0, 
                 games_played=0, games_won=0, games_lost=0, games_drawn=0):
        self.scores = scores
        self.steals = steals
        self.stolen_from = stolen_from
        self.team_passes_thrown = team_passes_thrown
        self.team_passes_received = team_passes_received
        self.intercepts_thrown = intercepts_thrown
        self.intercepts_received = intercepts_received
        self.blocks_thrown = blocks_thrown
        self.blocks_received = blocks_received
        self.assists_thrown = assists_thrown
        self.assists_received = assists_received
        self.games_played = games_played
        self.games_won = games_won
        self.games_lost = games_lost
        self.games_drawn = games_drawn
        
    # TODO: I can add properties here which perform queries to get other sorts of stats
    # Or, add another Stats class which is "filtered stats" or smthn like that, it has a filter
    # and then on init it get's a list of all team_ids that it should look for and then use `where team_id IN (TEAM_IDS)`
    # If this is the case, I would have a `@property` for everything which just queries over those team_ids
    # https://stackoverflow.com/questions/15041534/select-where-in-with-unknown-number-of-parameters
    
    @property
    def win_percentage(self):
        return self.games_won / self.games_played

    def __add__(self, other):
        if not isinstance(other, PlayerStats):
            raise NotImplementedError
        # Perform addition of fields between objects
        total_scores = self.scores + other.scores
        total_steals = self.steals + other.steals
        total_stolen_from = self.stolen_from + other.stolen_from
        total_team_passes_thrown = self.team_passes_thrown + other.team_passes_thrown
        total_team_passes_received = self.team_passes_received + other.team_passes_received
        total_intercepts_thrown = self.intercepts_thrown + other.intercepts_thrown
        total_intercepts_received = self.intercepts_received + other.intercepts_received
        total_blocks_thrown = self.blocks_thrown + other.blocks_thrown
        total_blocks_received = self.blocks_received + other.blocks_received
        total_assists_thrown = self.assists_thrown + other.assists_thrown
        total_assists_received = self.assists_received + other.assists_received
        total_games_played = self.games_played + other.games_played
        total_games_won = self.games_won + other.games_won
        total_games_lost = self.games_lost + other.games_lost
        total_games_drawn = self.games_drawn + other.games_drawn
        # Create a new PlayerStats object with the calculated totals
        result = PlayerStats(
            scores=total_scores,
            steals=total_steals,
            stolen_from=total_stolen_from,
            team_passes_thrown=total_team_passes_thrown,
            team_passes_received=total_team_passes_received,
            intercepts_thrown=total_intercepts_thrown,
            intercepts_received=total_intercepts_received,
            blocks_thrown=total_blocks_thrown,
            blocks_received=total_blocks_received,
            assists_thrown=total_assists_thrown,
            assists_received=total_assists_received,
            games_played=total_games_played,
            games_won=total_games_won,
            games_lost=total_games_lost,
            games_drawn=total_games_drawn
        )

        return result
    
    def is_empty(self):
        return (
            self.scores == 0 and
            self.steals == 0 and
            self.stolen_from == 0 and
            self.team_passes_thrown == 0 and
            self.team_passes_received == 0 and
            self.intercepts_thrown == 0 and
            self.intercepts_received == 0 and
            self.blocks_thrown == 0 and
            self.blocks_received == 0 and
            self.assists_thrown == 0 and
            self.assists_received == 0 and
            self.games_played == 0 and
            self.games_won == 0 and
            self.games_lost == 0 and
            self.games_drawn == 0
        )

    @staticmethod
    def get_player_total_stats(player_id, cursor = None):     
        if cursor is None:
            connection = get_db_connection()
            cursor = connection.cursor()
            close_cursor = True
        else:
            close_cursor = False

        def _execute_stat_query_and_get_total(query):
            cursor.execute(query, (player_id,))
            res = cursor.fetchone()
            if res is None:  # COUNT(*) should never really return NULL, but just in case
                return 0
            else:
                return res[0]
        
        stats = PlayerStats()
        try:
            SCORES_QUERY = "SELECT COUNT(*) from SCORE WHERE scorer = ?"
            stats.scores = _execute_stat_query_and_get_total(SCORES_QUERY)
            
            STEALER_QUERY = "SELECT COUNT(*) from STEAL WHERE stealer = ?"
            stats.steals = _execute_stat_query_and_get_total(STEALER_QUERY)
            
            STOLEN_FROM_QUERY = "SELECT COUNT(*) from STEAL WHERE victim = ?"
            stats.stolen_from = _execute_stat_query_and_get_total(STOLEN_FROM_QUERY)  
            
            TEAM_PASSES_THROWN_QUERY = "SELECT COUNT(*) from TEAMPASS WHERE passer = ?"
            stats.team_passes_thrown = _execute_stat_query_and_get_total(TEAM_PASSES_THROWN_QUERY)  
            
            TEAM_PASSES_RECEIVED_QUERY = "SELECT COUNT(*) from TEAMPASS WHERE catcher = ?"
            stats.team_passes_received = _execute_stat_query_and_get_total(TEAM_PASSES_RECEIVED_QUERY)     
            
            INTERCEPTS_THROWN_QUERY = "SELECT COUNT(*) from INTERCEPT WHERE passer = ?"
            stats.intercepts_thrown = _execute_stat_query_and_get_total(INTERCEPTS_THROWN_QUERY)     
            
            INTERCEPTS_RECEIVED_QUERY = "SELECT COUNT(*) from INTERCEPT WHERE catcher = ?"
            stats.intercepts_received = _execute_stat_query_and_get_total(INTERCEPTS_RECEIVED_QUERY)     
 
            BLOCKS_THROWN_QUERY = "SELECT COUNT(*) from BLOCK WHERE passer = ?"
            stats.blocks_thrown = _execute_stat_query_and_get_total(BLOCKS_THROWN_QUERY)     
            
            BLOCKS_RECEIVED_QUERY = "SELECT COUNT(*) from BLOCK WHERE catcher = ?"
            stats.blocks_received = _execute_stat_query_and_get_total(BLOCKS_RECEIVED_QUERY)      

            ASSISTS_THROWN_QUERY = "SELECT COUNT(*) from ASSIST WHERE passer = ?"
            stats.assists_thrown = _execute_stat_query_and_get_total(ASSISTS_THROWN_QUERY)     
            
            ASSISTS_RECEIVED_QUERY = "SELECT COUNT(*) from ASSIST WHERE catcher = ?"
            stats.assists_received = _execute_stat_query_and_get_total(ASSISTS_RECEIVED_QUERY)

            # Technically "games" just count as playing on a team once (so if there's a draw and the player played on both teams, they get 2 draws)
            GAMES_PLAYED_QUERY = "SELECT COUNT(*) from PlayerTeam WHERE steam_id = ?"
            stats.games_played = _execute_stat_query_and_get_total(GAMES_PLAYED_QUERY)        
            
            GAMES_WON_QUERY = "SELECT COUNT(*) from PlayerTeam LEFT JOIN TEAM on PlayerTeam.team_id = team.team_id where steam_id = ? AND winner = TRUE"
            stats.games_played = _execute_stat_query_and_get_total(GAMES_WON_QUERY)        
            
            GAMES_LOST_QUERY = "SELECT COUNT(*) from PlayerTeam LEFT JOIN TEAM on PlayerTeam.team_id = team.team_id where steam_id = ? AND winner = FALSE"
            stats.games_played = _execute_stat_query_and_get_total(GAMES_LOST_QUERY)        
            
            GAMES_DRAWN_QUERY = "SELECT COUNT(*) from Player LEFT JOIN TEAM on player.team_id = team.team_id LEFT JOIN TEAM as t2 ON team.game_id = t2.game_id AND team.team_id != t2.team_id where team.winner = t2.winner AND player.steam_id = ?"
            stats.games_played = _execute_stat_query_and_get_total(GAMES_DRAWN_QUERY)
            
            return stats
        finally:
            if close_cursor:
                cursor.close()

    def serialize(self):
        return {
            'scores': self.scores,
            'steals': self.steals,
            'stolen_from': self.stolen_from,
            'team_passes_thrown': self.team_passes_thrown,
            'team_passes_received': self.team_passes_received,
            'intercepts_thrown': self.intercepts_thrown,
            'intercepts_received': self.intercepts_received,
            'blocks_thrown': self.blocks_thrown,
            'blocks_received': self.blocks_received,
            'assists_thrown': self.assists_thrown,
            'assists_received': self.assists_received,
            'games_played': self.games_played,
            'games_won': self.games_won,
            'games_lost': self.games_lost,
            'games_drawn': self.games_drawn,
            'win_percentage': self.win_percentage
        }

class PlayerTeamStats():
    '''
    Stats of a player for a given team
    '''
    def __init__(self, scores=0, steals=0, stolen_from=0, team_passes_thrown=0, team_passes_received=0,
                 intercepts_thrown=0, intercepts_received=0, blocks_thrown=0, blocks_received=0, assists_thrown=0, assists_received=0):
        self.scores = scores
        self.steals = steals
        self.stolen_from = stolen_from
        self.team_passes_thrown = team_passes_thrown
        self.team_passes_received = team_passes_received
        self.intercepts_thrown = intercepts_thrown
        self.intercepts_received = intercepts_received
        self.blocks_thrown = blocks_thrown
        self.blocks_received = blocks_received
        self.assists_thrown = assists_thrown
        self.assists_received = assists_received
    
    def __add__(self, other):
        if not isinstance(other, PlayerTeamStats):
            raise NotImplementedError
        # Perform addition of fields between objects
        total_scores = self.scores + other.scores
        total_steals = self.steals + other.steals
        total_stolen_from = self.stolen_from + other.stolen_from
        total_team_passes_thrown = self.team_passes_thrown + other.team_passes_thrown
        total_team_passes_received = self.team_passes_received + other.team_passes_received
        total_intercepts_thrown = self.intercepts_thrown + other.intercepts_thrown
        total_intercepts_received = self.intercepts_received + other.intercepts_received
        total_blocks_thrown = self.blocks_thrown + other.blocks_thrown
        total_blocks_received = self.blocks_received + other.blocks_received
        total_assists_thrown = self.assists_thrown + other.assists_thrown
        total_assists_received = self.assists_received + other.assists_received

        # Create a new PlayerTeamStats object with the calculated totals
        result = PlayerTeamStats(
            scores=total_scores,
            steals=total_steals,
            stolen_from=total_stolen_from,
            team_passes_thrown=total_team_passes_thrown,
            team_passes_received=total_team_passes_received,
            intercepts_thrown=total_intercepts_thrown,
            intercepts_received=total_intercepts_received,
            blocks_thrown=total_blocks_thrown,
            blocks_received=total_blocks_received,
            assists_thrown=total_assists_thrown,
            assists_received=total_assists_received
        )

        return result
    
    def is_empty(self):
        return (
            self.scores == 0 and
            self.steals == 0 and
            self.stolen_from == 0 and
            self.team_passes_thrown == 0 and
            self.team_passes_received == 0 and
            self.intercepts_thrown == 0 and
            self.intercepts_received == 0 and
            self.blocks_thrown == 0 and
            self.blocks_received == 0 and
            self.assists_thrown == 0 and
            self.assists_received == 0
        )

    @staticmethod
    def get_player_team_stats(player_id, team_id, cursor = None):     
        if cursor is None:
            connection = get_db_connection()
            cursor = connection.cursor()
            close_cursor = True
        else:
            close_cursor = False

        def _execute_stat_query_and_get_total(query):
            cursor.execute(query, (player_id, team_id))
            res = cursor.fetchone()
            if res is None:  # COUNT(*) should never really return NULL, but just in case
                return 0
            else:
                return res[0]
        
        stats = PlayerTeamStats()
        try:
            SCORES_QUERY = "SELECT COUNT(*) from SCORE WHERE scorer = ? AND team_id = ?"
            stats.scores = _execute_stat_query_and_get_total(SCORES_QUERY)
            
            STEALER_QUERY = "SELECT COUNT(*) from STEAL WHERE stealer = ? AND stealer_team_id = ?"
            stats.steals = _execute_stat_query_and_get_total(STEALER_QUERY)
            
            STOLEN_FROM_QUERY = "SELECT COUNT(*) from STEAL WHERE victim = ? AND victim_team_id = ?"
            stats.stolen_from = _execute_stat_query_and_get_total(STOLEN_FROM_QUERY)  
            
            TEAM_PASSES_THROWN_QUERY = "SELECT COUNT(*) from TEAMPASS WHERE passer = ? AND team_id = ?"
            stats.team_passes_thrown = _execute_stat_query_and_get_total(TEAM_PASSES_THROWN_QUERY)  
            
            TEAM_PASSES_RECEIVED_QUERY = "SELECT COUNT(*) from TEAMPASS WHERE catcher = ? AND team_id = ?"
            stats.team_passes_received = _execute_stat_query_and_get_total(TEAM_PASSES_RECEIVED_QUERY)     
            
            INTERCEPTS_THROWN_QUERY = "SELECT COUNT(*) from INTERCEPT WHERE passer = ? AND passer_team_id = ?"
            stats.intercepts_thrown = _execute_stat_query_and_get_total(INTERCEPTS_THROWN_QUERY)     
            
            INTERCEPTS_RECEIVED_QUERY = "SELECT COUNT(*) from INTERCEPT WHERE catcher = ? AND catcher_team_id = ?"
            stats.intercepts_received = _execute_stat_query_and_get_total(INTERCEPTS_RECEIVED_QUERY)     
 
            BLOCKS_THROWN_QUERY = "SELECT COUNT(*) from BLOCK WHERE passer = ? AND passer_team_id = ?"
            stats.blocks_thrown = _execute_stat_query_and_get_total(BLOCKS_THROWN_QUERY)     
            
            BLOCKS_RECEIVED_QUERY = "SELECT COUNT(*) from BLOCK WHERE catcher = ? AND catcher_team_id = ?"
            stats.blocks_received = _execute_stat_query_and_get_total(BLOCKS_RECEIVED_QUERY)      

            ASSISTS_THROWN_QUERY = "SELECT COUNT(*) from ASSIST WHERE passer = ? AND team_id = ?"
            stats.assists_thrown = _execute_stat_query_and_get_total(ASSISTS_THROWN_QUERY)     
            
            ASSISTS_RECEIVED_QUERY = "SELECT COUNT(*) from ASSIST WHERE catcher = ? AND team_id = ?"
            stats.assists_received = _execute_stat_query_and_get_total(ASSISTS_RECEIVED_QUERY)          

            return stats
        finally:
            if close_cursor:
                cursor.close()

    def serialize(self):
        return {
            'scores': self.scores,
            'steals': self.steals,
            'stolen_from': self.stolen_from,
            'team_passes_thrown': self.team_passes_thrown,
            'team_passes_received': self.team_passes_received,
            'intercepts_thrown': self.intercepts_thrown,
            'intercepts_received': self.intercepts_received,
            'blocks_thrown': self.blocks_thrown,
            'blocks_received': self.blocks_received,
            'assists_thrown': self.assists_thrown,
            'assists_received': self.assists_received
        }

class Player():
    '''
    '''
    def __init__(self, steam_id, alias = None):
        self.steam_id = steam_id
        self.alias = alias
    
    @property
    def aliases(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        ALIAS_QUERY = "SELECT alias FROM PlayerTeam WHERE steam_id = ? GROUP BY alias"
        cursor.execute(ALIAS_QUERY, (self.steam_id,))
        res = cursor.fetchall()
        cursor.close()
        return [row[0] for row in res]
        
    @staticmethod
    def get_players_from_team_id(team_id, cursor = None):
        '''
        Returns a list of Player objects
        '''
        if cursor is None:
            connection = get_db_connection()
            cursor = connection.cursor()
            close_cursor = True
        else:
            close_cursor = False

        try:
            PLAYERS_QUERY = "SELECT steam_id, alias FROM PlayerTeam where team_id = ?"
            cursor.execute(PLAYERS_QUERY, (team_id,))
            res = cursor.fetchall()
            if len(res) == 0:
                raise PlayersNotFoundError()
            return [Player(row[0], row[1]) for row in res]
        finally:
            if close_cursor:
                cursor.close()

    def serialize(self):
        return {
            'steam_id': self.steam_id,
            'alias': self.alias
        }
                
    def __hash__(self):
        return self.steam_id

    def __eq__(self, other):
        if type(self) == type(other):
            return self.steam_id == other.steam_id
        return False

class TeamStats():
    """
    Stats for a whole team of players
    """
    def __init__(self, player_stats: dict[str, PlayerTeamStats]):
        self.player_stats = player_stats

    # TODO: Add other properties here which iterate through player_stats and get's stuff (like total goals)
    # don't forget to serialize them too

    @staticmethod
    def get_team_stats(team_id, players: list[Player] = None, cursor = None):     
        if cursor is None:
            connection = get_db_connection()
            cursor = connection.cursor()
            close_cursor = True
        else:
            close_cursor = False

        if players is None:
            players = Player.get_players_from_team_id(team_id, cursor)

        def _execute_stat_query_and_get_total(query):
            cursor.execute(query, (team_id,))
            res = cursor.fetchall()
            results = {}
            for row in res:
                results[row[0]] = row[1]
            return results
        
        try:
            player_stats = {}
            
            for player in players:
                player_stats[player.steam_id] = PlayerTeamStats()
                    
            SCORES_QUERY = "SELECT scorer, COUNT(*) from SCORE WHERE team_id = ? GROUP BY scorer"
            res = _execute_stat_query_and_get_total(SCORES_QUERY)
            for key, val in res.items():
                player_stats[key].scores = val
            
            STEALS_QUERY = "SELECT stealer, COUNT(*) from STEAL WHERE stealer_team_id = ? GROUP BY stealer"
            res = _execute_stat_query_and_get_total(STEALS_QUERY)
            for key, val in res.items():
                player_stats[key].steals = val
            
            STOLEN_FROM_QUERY = "SELECT victim, COUNT(*) from STEAL WHERE victim_team_id = ? GROUP BY victim"
            res = _execute_stat_query_and_get_total(STOLEN_FROM_QUERY)
            for key, val in res.items():
                player_stats[key].stolen_from = val

            TEAM_PASSES_THROWN_QUERY = "SELECT passer, COUNT(*) from TEAMPASS WHERE team_id = ? GROUP BY passer"
            res = _execute_stat_query_and_get_total(TEAM_PASSES_THROWN_QUERY)
            for key, val in res.items():
                player_stats[key].team_passes_thrown = val
            
            TEAM_PASSES_RECEIVED_QUERY = "SELECT catcher, COUNT(*) from TEAMPASS WHERE team_id = ? GROUP BY catcher"
            res = _execute_stat_query_and_get_total(TEAM_PASSES_RECEIVED_QUERY)
            for key, val in res.items():
                player_stats[key].team_passes_received = val

            INTERCEPTS_THROWN_QUERY = "SELECT passer, COUNT(*) from INTERCEPT WHERE passer_team_id = ? GROUP BY passer"
            res = _execute_stat_query_and_get_total(INTERCEPTS_THROWN_QUERY)
            for key, val in res.items():
                player_stats[key].intercepts_thrown = val
            
            INTERCEPTS_RECEIVED_QUERY = "SELECT catcher, COUNT(*) from INTERCEPT WHERE catcher_team_id = ? GROUP BY catcher"
            res = _execute_stat_query_and_get_total(INTERCEPTS_RECEIVED_QUERY)
            for key, val in res.items():
                player_stats[key].intercepts_received = val

            BLOCKS_THROWN_QUERY = "SELECT passer, COUNT(*) from BLOCK WHERE passer_team_id = ? GROUP BY passer"
            res = _execute_stat_query_and_get_total(BLOCKS_THROWN_QUERY)
            for key, val in res.items():
                player_stats[key].blocks_thrown = val
            
            BLOCKS_RECEIVED_QUERY = "SELECT catcher, COUNT(*) from BLOCK WHERE catcher_team_id = ? GROUP BY catcher"
            res = _execute_stat_query_and_get_total(BLOCKS_RECEIVED_QUERY)
            for key, val in res.items():
                player_stats[key].blocks_received = val

            ASSISTS_THROWN_QUERY = "SELECT passer, COUNT(*) from ASSIST WHERE team_id = ? GROUP BY passer"
            res = _execute_stat_query_and_get_total(ASSISTS_THROWN_QUERY)
            for key, val in res.items():
                player_stats[key].assists_thrown = val
            
            ASSISTS_RECEIVED_QUERY = "SELECT catcher, COUNT(*) from ASSIST WHERE team_id = ? GROUP BY catcher"
            res = _execute_stat_query_and_get_total(ASSISTS_RECEIVED_QUERY)
            for key, val in res.items():
                player_stats[key].assists_received = val      

            return TeamStats(player_stats)
        finally:
            if close_cursor:
                cursor.close()

    def serialize(self):
        return {player:stats.serialize() for player, stats in self.player_stats.items()}

class Team():
    '''
    This represent one team for one Game
    '''
    def __init__(self, team_id, team_name, players: list[Player]):
        self.id = team_id
        self.name = team_name
        self.players = players
        self._team_stats = None

    @property
    def team_stats(self):
        if self._team_stats is None:
            self._team_stats = TeamStats.get_team_stats(team_id = self.id, players = self.players)
        return self._team_stats
 
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'players': [p.serialize() for p in self.players],
            # TODO: consider moving each PlayerTeamStats in team_stats to the 'players' list
            # 'players': [p.serialize() | {"stats":self.team_stats.player_stats[p.steam_id]} for p in self.players],
            'team_stats': self.team_stats.serialize()
        }
 
    @staticmethod
    def parse_and_store(team: dict):
        name = team["name"]
        players = Players.parse_and_store(team["players"])

    @staticmethod
    def get_teams_from_game_id(game_id, cursor = None):
        '''
        Returns a tuple of (blu_team, red_team, game_result)
        blu_team and red_team are both Team objects
        game_result is a GameResult object
        '''
        if cursor is None:
            connection = get_db_connection()
            cursor = connection.cursor()
            close_cursor = True
        else:
            close_cursor = False

        try:
            TEAMS_QUERY = "SELECT team_id, team_name, winner FROM Team where game_id = ? ORDER BY team_color"
            cursor.execute(TEAMS_QUERY, (game_id,))
            res = cursor.fetchall()
            if len(res) != 2:
                raise TeamNotFoundError()
            blu_team_id = res[0][0]
            blu_team_name = res[0][1]
            blu_team_winner = res[0][2]
            blu_team = Team(blu_team_id, blu_team_name, Player.get_players_from_team_id(blu_team_id, cursor))
            red_team_id = res[1][0]
            red_team_name = res[1][1]
            red_team_winner = res[1][2]
            red_team = Team(red_team_id, red_team_name, Player.get_players_from_team_id(red_team_id, cursor))
            if blu_team_winner == red_team_winner:
                game_result = GameResult.DRAW
            elif blu_team_winner:
                game_result = GameResult.BLU_VICTORY
            else:
                game_result = GameResult.RED_VICTORY
            return blu_team, red_team, game_result
        finally:
            if close_cursor:
                cursor.close()
                
    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if type(self) == type(other):
            return self.id == other.id
        return False

class Game():
    '''
    '''
    def __init__(self, game_id, game_date, game_duration, game_map, blu_team: Team, red_team: Team, game_result: GameResult):
        self.id = game_id
        self.date = game_date
        self.duration = game_duration
        self.map = game_map
        self.blu_team = blu_team
        self.red_team = red_team
        self.game_result = game_result

    @staticmethod
    def parse_and_store_game(game: dict):
        # TODO PARSE THESE
        date = game["date"]
        duration = game["duration"]
        map = game["map"]
        game_result = GameResult.parse(game["game_result"])

        # create game in db
        pass

        # probably pass in cursor (and idk how to make it know who the winner is)
        blu_team = Team.parse_and_store(game["blu_team"])
        red_team = Team.parse_and_store(game["red_team"])


    @staticmethod
    def get_game(game_id, cursor = None):
        if cursor is None:
            connection = get_db_connection()
            cursor = connection.cursor()
            close_cursor = True
        else:
            close_cursor = False

        try:
            GAME_INFO_QUERY = "SELECT game_date, game_duration, game_map from GAME WHERE game_id = ?"
            cursor.execute(GAME_INFO_QUERY, (game_id,))
            res = cursor.fetchone()
            if res is None:
                raise GameNotFoundError()
            # TODO: PARSE THESE
            game_date = res[0]
            game_duration = res[1]
            game_map = res[2]

            blu_team, red_team, game_result = Team.get_teams_from_game_id(game_id, cursor)
            return Game(game_id, game_date, game_duration, game_map, blu_team, red_team, game_result)
        finally:
            if close_cursor:
                cursor.close()
  
    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if type(self) == type(other):
            return self.id == other.id
        return False

    def serialize(self):
        return {
            "id": self.id,
            "date": self.date,
            "duration": self.duration,
            "map": self.map,
            "blu_team": self.blu_team.serialize(),
            "red_team": self.red_team.serialize(),
            "game_result": self.game_result
        }


# Ok, so the only thing we really INSERT into the database right now could be Players and Games, so no need to make it too complicated

