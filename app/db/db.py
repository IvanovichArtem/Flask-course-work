from psycopg2 import connect
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, db_name, user, password, host="localhost", port="5432"):
        self.conn = connect(dbname=db_name, host=host, user=user, password=password, port=port)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def all(self, **kwargs):
        self.cursor.execute(f"SELECT * FROM {kwargs['table_name']}")
        fetch = self.cursor.fetchall()
        return fetch 
    
    def last_login(self, **kwargs):
        self.cursor.execute(f"UPDATE {kwargs['table_name']} SET last_login=current_timestamp where username = '{kwargs['username']}'")
        self.conn.commit()

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
                if type(value) is str:
                    query_expression.append(f"{key} = '{value}'")
                    continue
                else:
                    query_expression.append(f"{key} = {value}")
                    continue
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
    
    def create(self, table_name, **kwargs):
        """INSERT INTO user_user(username,last_name,password,first_name,email)
           VALUES('username','last_name','password','first','email');"""
        keys = [str(i) for i in kwargs.keys()]
        values = [f"'{i}'" for i in kwargs.values()]
        self.cursor.execute(f"INSERT INTO {table_name}({','.join(keys)}) VALUES({','.join(values)})")
        self.conn.commit()
        
    def exists(self, table_name, **kwargs):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        fetch = self.cursor.fetchall()
        for row in fetch:
            arr = [row[i] == kwargs[i] for i in kwargs.keys() if row[i] == kwargs[i]]
            if sum(arr) == len(kwargs):
                return True
        return False

    def update(self, table_name, key, key_value, **kwargs):
        """UPDATE weather SET 
        (first_name, last_name, img) = (first_name, last_name, img)
  WHERE id=id;"""
        keys = [str(i) for i in kwargs.keys()]
        values = [f"'{i}'" if (type(i) is str) else f"{i}" for i in kwargs.values()]
        if len(kwargs) == 1:
            query = f"UPDATE {table_name} SET {','.join(keys)} = {','.join(values)} WHERE {key}={key_value};"
        else:
            query = f"UPDATE {table_name} SET ({','.join(keys)}) = ({','.join(values)}) WHERE {key}={key_value};"
        self.cursor.execute(query)
        self.conn.commit()
    
    def get_user_id(self, table_name, **kwargs):
        key = list(kwargs.keys())[0]
        value = kwargs.get(key)
        query = f"SELECT id from {table_name} WHERE {key} = '{value}'"
        self.cursor.execute(query)
        fetch = self.cursor.fetchone()
        return fetch['id']
    
    def query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

if __name__ == "__main__":
    db = Database(db_name="flask_museum", user="admin", password="root")
    db.get_user_id(table_name='user_user', username='Lagrush')
