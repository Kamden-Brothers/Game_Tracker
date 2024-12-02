import psycopg2

class DB:
    def __init__(self):
        self.connect()
    
    def connect(self):
        self.connection = psycopg2.connect(dbname='statistics', user='postgres', password='games')
        
    def execute(self, query_text, record=(), commit=False, select_all=False):
        cursor = self.connection.cursor()
        cursor.execute(query_text, record)
        if select_all:
            game_info = cursor.fetchall()
        else:
            game_info = cursor.fetchone()

        if commit:
            self.connection()
        cursor.close()
        return game_info