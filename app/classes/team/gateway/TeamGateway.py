from psycopg2.extensions import connection

class TeamGateway:
    def __init__(self, db: connection):
        self.db = db

    def get_all_teams(self):
        '''
        Get all team data
        '''
        with self.db.cursor() as cur:
            cur.execute('''SELECT team_name, p_1.username, p_2.username FROM public.team
                           LEFT JOIN public.player as p_1 on p_1.player_id = team.player_1
                           LEFT JOIN public.player as p_2 on p_2.player_id = team.player_2''')
            return {team[0]: team[1:] for team in cur.fetchall()}

    def update_team(self, team_name: str, player1: int, player2: int):
        with self.db.cursor() as cur:
            cur.execute(
                """
                UPDATE team
                SET team_name = %s
                WHERE player_1 = %s AND player_2 = %s
                """,
                (team_name, player1, player2)
            )

            return cur.rowcount

    def insert_team(self, team_name: str, player_1: int, player_2: int):
        with self.db.cursor() as cur:
            query_str = """INSERT INTO team (team_name, player_1, player_2)
                VALUES (%s, %s, %s)
            """

            cur.execute(query_str, (team_name, player_1, player_2))

    def delete_team(self, team_name):
        with self.db.cursor() as cur:
            cur.execute(
                """
                DELETE FROM team
                WHERE team_name = %s
                """,
                (team_name, )
            )

            return cur.rowcount
