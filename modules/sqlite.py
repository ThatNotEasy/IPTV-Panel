import sqlite3
from modules.config import setup_config

config = setup_config()
DATABASE = config['SQLITE']["DATABASE"]

class SQLITE:
    def __init__(self):
        self.dbname = DATABASE
        self.conn = None
        self.cur = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.dbname)
            self.cur = self.conn.cursor()
        except Exception as err:
            print(f"Error at connection, Error info: {err}")

    def query(self, sql, args=(), one=False):
        try:
            self.cur.execute(sql, args)
            if 'SELECT' in sql.upper():
                r = [dict((self.cur.description[i][0], value) \
                          for i, value in enumerate(row)) for row in self.cur.fetchall()]
                return (r[0] if r else None) if one else r
        except Exception as err:
            print(f"Error executing query: {err}")

    def execute(self, sql, args=()):
        try:
            self.cur.execute(sql, args)
        except Exception as err:
            print(f"Error executing query: {err}")

    def commit(self):
        try:
            self.conn.commit()
        except Exception as err:
            print(f"Error committing transaction: {err}")

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception as err:
            print(f"Error closing connection: {err}")
            
    def create_tables(self):
        table_definitions = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    login_date TIMESTAMP,
                    last_login_date TIMESTAMP
                )
            '''
        }
        for table_name, create_sql in table_definitions.items():
            self.execute(create_sql)
        self.commit()