from psycopg2 import connect
from psycopg2.extras import RealDictCursor
class Database:
    def __init__(self, db_name, user, password, host="localhost", port="5432"):
        self.conn = connect(dbname=db_name, host=host, user=user, password=password, port=port)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def all(self, **kwargs):
        self.cursor.execute(f"SELECT * FROM {kwargs['table_name']}")
        fetch = self.cursor.fetchall()
        return fetch 
    
    def filter(self, **kwargs):
        """sumary_line
        
        Keyword arguments:
        table_name - required -> Str
        other_conditions:
            id=1 \n
            id__gt=4 ---> id > 4 \n
            id__gte=4 ---> id >= 4 \n
            id__lt=4 ---> id < 4 \n
            id__lte=4 ---> id <= 4 \n
            id__in=(1,2,3) ---> id IN (1, 2, 3) \n

        Return: fetch
        """
        table_name = kwargs['table_name']
        del kwargs['table_name']
        query_expression = []
        for key, value in kwargs.items():
            if "__" in key:
                prefix, postfix = key.split('__')
            else:
                query_expression.append(f"{key} = {value}")
                break
            if postfix == "gt":
                query_expression.append(f"{prefix} > {value}")
            elif postfix == "gte":
                query_expression.append(f"{prefix} >= {value}")
            elif postfix == "lt":
                query_expression.append(f"{prefix} < {value}")
            elif postfix == "lte":
                query_expression.append(f"{prefix} <= {value}")
            elif postfix == "in":
                query_expression.append(f"{prefix} IN {value}")

        self.cursor.execute(f"SELECT * FROM {table_name} WHERE {' AND '.join(query_expression)}")
        fetch = self.cursor.fetchall()

        return fetch
    


    def exists(self, table_name, **kwargs):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        fetch = self.cursor.fetchall()
        for row in fetch:
            arr = [row[i] == kwargs[i] for i in kwargs.keys() if row[i] == kwargs[i]]
            if sum(arr) == len(kwargs):
                return True
        return False


if __name__ == "__main__":
    db = Database(db_name="flask_museum", user="admin", password="root")
    print(db.filter(table_name="catalog_exhibition", type_id=1))