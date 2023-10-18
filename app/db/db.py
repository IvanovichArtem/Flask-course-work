from psycopg2 import connect

class Database:
    def __init__(self, db_name, user, password, host="localhost", port="5432"):
        self.conn = connect(dbname=db_name, host=host, user=user, password=password, port=port)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def all(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        print(self.cursor.fetchall())

if __name__ == "__main__":
    db = Database(db_name="flask_museum", user="admin", password="root")
    db.all("user_user")