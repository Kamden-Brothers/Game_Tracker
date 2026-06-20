from psycopg2.extensions import connection

class PinochleGateway:
    def __init__(self, db: connection):
        self.db = db

    def get_games_for_matchup(self, team_id_1: int, team_id_2: int) -> dict:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT game_date, game_of_day FROM game
                WHERE team_1 = %s AND team_2 = %s
                """,
                (team_id_1, team_id_2)
            )

            return [f'{game[0].strftime('%m-%d-%Y')}.{game[1]}' for game in cur.fetchall()]

    def get_next_match_number(self, team_id_1: int, team_id_2: int):
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(game_of_day), 0) + 1
                FROM game
                WHERE team_1 = %s AND team_2 = %s
                """,
                (team_id_1, team_id_2)
            )

            return cur.fetchone()[0]

    def create_game(self, team_id_1: int, team_id_2: int, game_date: str, game_of_day: int):
        with self.db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game
                (team_1, team_2, game_date, game_of_day)
                VALUES (%s, %s, %s, %s)
                """,
                (team_id_1, team_id_2, game_date, game_of_day)
            )

            return cur.rowcount
    
    def get_game_id(self, team_id_1: int, team_id_2: int, game_date: str, game_of_day: int) -> int|None:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT game_id FROM game
                WHERE team_1 = %s AND team_2 = %s AND game_date = %s AND game_of_day = %s
                """,
                (team_id_1, team_id_2, game_date, game_of_day)
            )

            row = cur.fetchone()
            return row[0] if row else None

    def load_game(self, game_id):
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT round_number, trump, bid, username, meld_1, meld_2, tricks_1, tricks_2 FROM round
                JOIN player ON top_bidder = player_id
                WHERE game_id = %s
                """,
                (game_id, )
            )

            return [{
                'round_number': round[0],
                'trump': round[1],
                'bid': round[2],
                'top_bidder': round[3],
                'meld_1': round[4],
                'meld_2': round[5],
                'tricks_1': round[6],
                'tricks_2': round[7]
            } for round in cur.fetchall()]

    def delete_game(self, team_id_1: int, team_id_2: int, game_date: str, game_of_day: int):
        with self.db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM game
                WHERE team_1 = %s AND team_2 = %s AND game_date = %s AND game_of_day = %s
                """,
                (team_id_1, team_id_2, game_date, game_of_day)
            )

            return cur.rowcount
