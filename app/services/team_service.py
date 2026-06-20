from app.services.player_service import PlayerService
from app.classes.team.Team import Team
from app.classes.team.gateway.TeamGateway import TeamGateway

class TeamService:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @staticmethod
    def get_class(conn) -> Team:
        return Team(TeamGateway(conn), PlayerService.get_class(conn))

    def get_all_teams(self):
        with self.db_pool.connection() as conn:
            team = self.get_class(conn)
            return team.get_all_teams()

    def submit_team(self, data):
        with self.db_pool.connection() as conn:
            team = self.get_class(conn)
            return team.submit_team(data)

    def delete_team(self, data):
        with self.db_pool.connection() as conn:
            team = self.get_class(conn)
            return team.delete_team(data)
