import sqlite3

# Connect to the database (or create if it doesn't exist)
conn = sqlite3.connect("passtime_stats.db")  # Replace with the desired database filename
cursor = conn.cursor()

# Create the Game table
cursor.execute('''
CREATE TABLE Game (
    game_id INTEGER PRIMARY KEY,
    game_date DATE,
    game_duration TIME,
    game_map TEXT
)
''')

# Create the Team table
cursor.execute('''
CREATE TABLE Team (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT,
    team_color TEXT CHECK( team_color IN ('RED', 'BLU') ),
    game_id INTEGER,
    winner INTEGER,
    FOREIGN KEY (game_id) REFERENCES Game(game_id)
)
''')

# Create the PlayerTeam table
cursor.execute('''
CREATE TABLE PlayerTeam (
    steam_id INTEGER,
    team_id INTEGER,
    alias TEXT,
    PRIMARY KEY (player_id, team_id),
    FOREIGN KEY (team_id) REFERENCES Team(team_id)
)
''')

# Create the TeamPass table
cursor.execute('''
CREATE TABLE TeamPass (
    pass_id INTEGER PRIMARY KEY,
    team_id INTEGER,
    passer INTEGER,
    catcher INTEGER,
    FOREIGN KEY (team_id) REFERENCES Team(team_id),
    FOREIGN KEY (passer) REFERENCES PlayerTeam(steam_id),
    FOREIGN KEY (catcher) REFERENCES PlayerTeam(steam_id)
)
''')

# Create the Assist table
cursor.execute('''
CREATE TABLE Assist (
    assist_id INTEGER PRIMARY KEY,
    team_id INTEGER,
    passer INTEGER,
    catcher INTEGER,
    FOREIGN KEY (team_id) REFERENCES Team(team_id),
    FOREIGN KEY (passer) REFERENCES PlayerTeam(steam_id),
    FOREIGN KEY (catcher) REFERENCES PlayerTeam(steam_id)
)
''')

# Create the Block table
cursor.execute('''
CREATE TABLE Block (
    block_id INTEGER PRIMARY KEY,
    passer_team_id INTEGER,
    catcher_team_id INTEGER,
    passer INTEGER,
    catcher INTEGER,
    FOREIGN KEY (passer_team_id) REFERENCES Team(team_id),
    FOREIGN KEY (catcher_team_id) REFERENCES Team(team_id),
    FOREIGN KEY (passer) REFERENCES PlayerTeam(steam_id),
    FOREIGN KEY (catcher) REFERENCES PlayerTeam(steam_id)
)
''')

# Create the Intercept table
cursor.execute('''
CREATE TABLE Intercept (
    intercept_id INTEGER PRIMARY KEY,
    passer_team_id INTEGER,
    catcher_team_id INTEGER,
    passer INTEGER,
    catcher INTEGER,
    FOREIGN KEY (passer_team_id) REFERENCES Team(team_id),
    FOREIGN KEY (catcher_team_id) REFERENCES Team(team_id),
    FOREIGN KEY (passer) REFERENCES PlayerTeam(steam_id),
    FOREIGN KEY (catcher) REFERENCES PlayerTeam(steam_id)
)
''')

# Create the Steal table
cursor.execute('''
CREATE TABLE Steal (
    steal_id INTEGER PRIMARY KEY,
    victim_team_id INTEGER,
    stealer_team_id INTEGER,
    victim INTEGER,
    stealer INTEGER,
    FOREIGN KEY (victim_team_id) REFERENCES Team(team_id),
    FOREIGN KEY (stealer_team_id) REFERENCES Team(team_id),
    FOREIGN KEY (victim) REFERENCES PlayerTeam(steam_id),
    FOREIGN KEY (stealer) REFERENCES PlayerTeam(steam_id)
)
''')

# Create the Score table
cursor.execute('''
CREATE TABLE Score (
    score_id INTEGER PRIMARY KEY,
    team_id INTEGER,
    scorer INTEGER,
    FOREIGN KEY (team_id) REFERENCES Team(team_id),
    FOREIGN KEY (scorer) REFERENCES PlayerTeam(steam_id)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("PasstimeStats database created successfully.")
