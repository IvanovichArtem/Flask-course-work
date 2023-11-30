from passlib.hash import pbkdf2_sha256
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

conn = SQLAlchemy()


def all(table_name):
    engine = conn.engine.connect()
    result = engine.execute(text(f"SELECT * FROM {table_name}"))
    return result.mappings().all()


def last_login(**kwargs):
    engine = conn.engine.connect()
    engine.execute(
        text(
            f"UPDATE {kwargs['table_name']} SET last_login=current_timestamp where username = '{kwargs['username']}'"
        )
    )
    engine.commit()


def filter(table_name: str, **kwargs):
    """sumary_line
    id=1 \n
    id__gt=4 ---> id > 4 \n
    id__gte=4 ---> id >= 4 \n
    id__lt=4 ---> id < 4 \n
    id__lte=4 ---> id <= 4 \n
    id__in=(1,2,3) ---> id IN (1, 2, 3) \n
    """
    engine = conn.engine.connect()
    query_expression = []
    for key, value in kwargs.items():
        if "__" in key:
            prefix, postfix = key.split("__")
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

    result = engine.execute(
        text(
            f"SELECT * FROM {table_name} WHERE {' AND '.join(query_expression)}"
        )
    )
    return result.mappings().all()


def query(query, r=False):
    engine = conn.engine.connect()
    result = engine.execute(text(query))
    return result.mappings().all() if r else None


def create(table_name: str, **kwargs):
    """INSERT INTO user_user(username,last_name,password,first_name,email)
    VALUES('username','last_name','password','first','email');"""
    engine = conn.engine.connect()
    keys = [str(i) for i in kwargs.keys()]
    values = [f"'{i}'" for i in kwargs.values()]
    engine.execute(
        text(
            f"INSERT INTO {table_name}({','.join(keys)}) VALUES({','.join(values)})"
        )
    )
    engine.commit()


def delete(table_name: str, condition: str):
    engine = conn.engine.connect()
    query = text(f"DELETE FROM {table_name} WHERE {condition}")
    engine.execute(query)
    engine.commit()


def exists(table_name: str, **kwargs):
    engine = conn.engine.connect()
    fetch = engine.execute(text(f"SELECT * FROM {table_name}")).mappings().all()
    for row in fetch:
        arr = [
            row[i] == kwargs[i] for i in kwargs.keys() if row[i] == kwargs[i]
        ]
        if sum(arr) == len(kwargs):
            return True
    return False


def update(table_name: str, key, key_value, **kwargs):
    """UPDATE weather SET
            (first_name, last_name, img) = (first_name, last_name, img)
    WHERE id=id;"""
    engine = conn.engine.connect()
    keys = [str(i) for i in kwargs.keys()]
    values = [f"'{i}'" if (type(i) is str) else f"{i}" for i in kwargs.values()]
    if len(kwargs) == 1:
        query = text(
            f"UPDATE {table_name} SET {','.join(keys)} = {','.join(values)} WHERE {key}={key_value};"
        )
    else:
        query = text(
            f"UPDATE {table_name} SET ({','.join(keys)}) = ({','.join(values)}) WHERE {key}={key_value};"
        )
    engine.execute(query)
    engine.commit()


def get_user_id(table_name: str, **kwargs):
    engine = conn.engine.connect()
    key = list(kwargs.keys())[0]
    value = kwargs.get(key)
    query = text(f"SELECT id from {table_name} WHERE {key} = '{value}'")
    engine.execute(query)
    fetch = engine.fetchone()
    return fetch["id"]


def insert(query: str):
    engine = conn.engine.connect()
    engine.execute(text(query))
    engine.commit()


def code(password):
    return pbkdf2_sha256.hash(password)


def verify_password(input_password, hash):
    return pbkdf2_sha256.verify(input_password, hash)


def get_user_id(table_name: str, **kwargs):
    engine = conn.engine.connect()
    key = list(kwargs.keys())[0]
    value = kwargs.get(key)
    query = text(f"SELECT id from {table_name} WHERE {key} = '{value}'")
    fetch = engine.execute(query).mappings().one()

    return fetch["id"]


# def export(self):
#     engine.execute(
#         "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
#     )
#     tables = engine.mappings().all()

#     for table in tables:
#         table_name = table["table_name"]
#         export_file_name = f"{table_name}.json"
#         engine.execute(f"SELECT * FROM {table_name}")
#         rows = engine.mappings().all()
#         with open(export_file_name, "w", encoding="utf-8") as export_file:
#             json.dump(
#                 rows, export_file, ensure_ascii=False, cls=DateTimeEncoder
#             )


# db = Database(conn=conn)
# db.query("select * from user_user", True)
# del db
