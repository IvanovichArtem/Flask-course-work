from psycopg2 import connect
from psycopg2.extras import RealDictCursor
class Database:
    def __init__(self, db_name, user, password, host="localhost", port="5432"):
        self.conn = connect(dbname=db_name, host=host, user=user, password=password, port=port)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def all(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        fetch = self.cursor.fetchall()
        return fetch 
    
    def filter(self, table_name, filter_conditions="TRUE"):
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE {filter_conditions}")
        fetch = self.cursor.fetchall()

        return fetch


if __name__ == "__main__":
    db = Database(db_name="flask_museum", user="admin", password="root")
    db.filter("catalog_exhibition", "type_id=2")