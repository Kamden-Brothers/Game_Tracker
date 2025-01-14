import json

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from utils import LoadCredentials


def create_database_and_tables():
    credentials = LoadCredentials.get_connection_credentials()
    dbname = 'Pinchole'

    def create_database():
        try:
            # Able to connect to database
            connect_to_db(dbname)
        except Exception as e:
            # Not able to connect, Create database
            print('Could not connect to database. Trying to create')
            conn = psycopg2.connect(dbname='postgres',
                  user=credentials['username'], host='',
                  password=credentials['password'])

            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE

            cur = conn.cursor()
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(dbname))
                )
            cur.close()
            conn.close()


    def create_tables():
        commands = (
            '''        
            CREATE TABLE Player (
                player_id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                first_name VARCHAR(255) NOT NULL
                )
            ''',
            '''        
            CREATE TABLE Team (
                team_id SERIAL PRIMARY KEY,
                player_1 INTEGER,
                player_2 INTEGER,
                team_name VARCHAR(255) NOT NULL UNIQUE,
                CONSTRAINT cn_player_1_fk
                    FOREIGN KEY (player_1)
                    REFERENCES Player (player_id),
                CONSTRAINT cn_player_2_fk
                    FOREIGN KEY (player_2)
                    REFERENCES Player (player_id),
                CONSTRAINT cn_enforce_team_order_ck
                    CHECK (player_1 < player_2),
                CONSTRAINT cn_unique_teams
                    UNIQUE (player_1, player_2)
                )
            ''',
            '''        
            CREATE TABLE Game (
                game_id SERIAL PRIMARY KEY,
                team_1 INTEGER,
                team_2 INTEGER,
                game_date DATE NOT NULL,
                game_of_day INTEGER NOT NULL,
                CONSTRAINT cn_team_1_fk
                    FOREIGN KEY (team_1)
                    REFERENCES Team (team_id),
                CONSTRAINT cn_team_2_fk
                    FOREIGN KEY (team_2)
                    REFERENCES Team (team_id),
                CONSTRAINT cn_enforce_team_order_ck
                    CHECK (team_1 < team_2),
                CONSTRAINT cn_unique_games
                    UNIQUE (team_1, team_2, date, game_of_day)
                )
            ''',
            '''
            CREATE TABLE Suit (
                suit VARCHAR(8) PRIMARY KEY
                )
            ''',
            '''
            CREATE TABLE Round (
                round_number INTEGER,
                game_id INTEGER,
                trump VARCHAR(8) NOT NULL,
                bid INTEGER NOT NULL,
                top_bidder INTEGER NOT NULL,
                meld_1 INTEGER NOT NULL,
                meld_2 INTEGER NOT NULL,
                tricks_1 INTEGER NOT NULL,
                tricks_2 INTEGER NOT NULL,
                CONSTRAINT cn_game_pk
                    FOREIGN KEY (game_id)
                    REFERENCES Game (game_id)
                    ON DELETE CASCADE,
                CONSTRAINT cn_trump_fk
                    FOREIGN KEY (trump)
                    REFERENCES Suit (suit),
                CONSTRAINT cn_topbid_fk
                    FOREIGN KEY (top_bidder)
                    REFERENCES Player (player_id),
                CONSTRAINT cn_min_bid
                    CHECK (bid > 49),
                PRIMARY KEY(round_number, game_id)
                )
            '''
            )
        try:
            with connect_to_db(dbname) as conn:
                with conn.cursor() as cur:
                    # execute the CREATE TABLE statement
                    for command in commands:
                        cur.execute(command)
        except (psycopg2.DatabaseError, Exception) as error:
            print(error)

    # Checks if it can connect to db. If not it throws an exception
    create_database()

    # Previously created tables will cause exception
    create_tables()


def connect_to_db(dbname):
    credentials = LoadCredentials.get_connection_credentials()
    con = psycopg2.connect(dbname=dbname,
          user=credentials['username'], host='',
          password=credentials['password'])
    return con