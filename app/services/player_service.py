from app.classes.player.Player import Player

class PlayerService:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    def get_all_players(self):
        with self.db_pool.connection() as conn:
            player = Player(conn)
            return player.get_all_players()

    def submit_player(self, data):
        with self.db_pool.connection() as conn:
            player = Player(conn)
            return player.submit_player(data)

    def delete_player(self, data):
        with self.db_pool.connection() as conn:
            player = Player(conn)
            return player.delete_player(data)
