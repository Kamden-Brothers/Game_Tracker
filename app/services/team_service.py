from app.classes.player.Player import Player
from app.classes.team.Team import Team

class TeamService:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @staticmethod
    def build_team_class(conn):
        team = Player(conn)
        return Team(conn, team)
        

    def get_all_teams(self):
        with self.db_pool.connection() as conn:
            team = self.build_team_class(conn)
            return team.get_all_teams()

    def submit_team(self, data):
        with self.db_pool.connection() as conn:
            team = self.build_team_class(conn)
            return team.submit_team(data)

    def delete_team(self, data):
        with self.db_pool.connection() as conn:
            team = self.build_team_class(conn)
            return team.delete_team(data)
