from psycopg2.extensions import connection

class PlayerGateway:
    def __init__(self, db: connection):
        self.db = db

    def get_all_players(self):
        '''
        Get all player data
        '''
        with self.db.cursor() as cur:
            cur.execute('SELECT username, first_name FROM public.player')
            return {player[0]: player[1:] for player in cur.fetchall()}
    
    def get_player_id(self, username):
        '''
        Get a player id from there username
        '''
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT player_id FROM public.player
                WHERE username = %s
                """,
                (username, )
            )

            return cur.fetchone()

    def update_player(self, username, first_name, previous_username):
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE player
                SET username = %s,
                    first_name = %s
                WHERE username = %s
                """,
                (username, first_name, previous_username)
            )

            return cur.rowcount
            
    def insert_player(self, username, first_name):
        with self.db.cursor() as cur:
            query_str = """INSERT INTO player (username, first_name)
                VALUES (%s, %s)
            """

            cur.execute(query_str, (username, first_name))

    def delete_player(self, username):
        with self.db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM player
                WHERE username = %s
                """,
                (username,)
            )

            return cur.rowcount
