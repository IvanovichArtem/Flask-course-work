from passlib.hash import pbkdf2_sha256
from datetime import datetime
import os
import matplotlib.pyplot as plt
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self, db_name, user, password, host, port):
        self.conn = connect(
            dbname=db_name, host=host, user=user, password=password, port=port
        )
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
        self.cursor.execute(
            f"UPDATE {kwargs['table_name']} SET last_login=current_timestamp where id = '{kwargs['id']}'"
        )
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
        table_name = kwargs["table_name"]
        del kwargs["table_name"]
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

        self.cursor.execute(
            f"SELECT * FROM {table_name} WHERE {' AND '.join(query_expression)}"
        )
        fetch = self.cursor.fetchall()

        return fetch

    def create(self, table_name, **kwargs):
        """INSERT INTO user_user(username,last_name,password,first_name,email)
        VALUES('username','last_name','password','first','email');"""
        keys = [str(i) for i in kwargs.keys()]
        values = [f"'{i}'" for i in kwargs.values()]
        self.cursor.execute(
            f"INSERT INTO {table_name}({','.join(keys)}) VALUES({','.join(values)})"
        )
        self.conn.commit()

    def exists(self, table_name, **kwargs):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        fetch = self.cursor.fetchall()
        for row in fetch:
            arr = [
                row[i] == kwargs[i]
                for i in kwargs.keys()
                if row[i] == kwargs[i]
            ]
            if sum(arr) == len(kwargs):
                return True
        return False

    def update(self, table_name, key, key_value, **kwargs):
        """UPDATE weather SET
              (first_name, last_name, img) = (first_name, last_name, img)
        WHERE id=id;"""
        keys = [str(i) for i in kwargs.keys()]
        values = [
            f"'{i}'" if (type(i) is str) else f"{i}" for i in kwargs.values()
        ]
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
        return fetch["id"]

    def query(self, query, r=False):
        self.cursor.execute(query)
        return self.cursor.fetchall() if r else self.conn.commit()

    def create_json(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        json_filename = f"flask_museum_json_{timestamp}.json"
        table_names = self.query(
            """SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'""",
            True,
        )
        table_names = [value["table_name"] for value in table_names]
        with open(os.path.join("media/db", json_filename), "w") as f:
            for name in table_names:
                json_text = self.query(
                    f"""SELECT json_agg(t) FROM (
                    SELECT * FROM {name}
                    ) t;""",
                    True,
                )[0]["json_agg"]
                if json_text:
                    f.write(str(json_text).replace("'", '"'))
        return json_filename

    def create_pdf(data: dict):
        months = list(data.keys())
        values = list(data.values())

        plt.bar(months, values)
        plt.xlabel("Месяц")
        plt.ylabel("Значение")
        plt.title("График данных по месяцам")
        name = str(datetime.now())
        plt.savefig(f"media/pdf/{name}.pdf")
        return f"{name}.pdf"

    def code(self, password):
        return pbkdf2_sha256.hash(password)

    def verify_password(input_password, hash):
        return pbkdf2_sha256.verify(input_password, hash)

    def delete(self, table_name: str, condition: str):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query)
        self.conn.commit()

    def get(self, table_name, id, name):
        self.cursor.execute(f"SELECT {name} FROM {table_name} WHERE id = {id}")
        return self.cursor.fetchone()[name]

    def insert(self, query: str):
        self.cursor.execute(query)
        self.conn.commit()

    def get_last_users(self):
        result = self.query(
            """SELECT u.username as "Логин", u.last_login as "Последний раз зашел", u.first_name as "Имя",
            u.last_name AS "Фамилия", COUNT(oe.id) AS "Кол-во купленных билетов",
            COUNT(op.id) as "Кол-во купленных товаров",
            MAX(oe.book_date) AS "Дата последнего заказа"
    FROM user_user AS u
    LEFT JOIN order_exhibition AS oe ON u.id = oe.user_id
    LEFT JOIN order_products AS op ON u.id = op.user_id
    GROUP BY u.id
    ORDER BY u.last_login DESC
    LIMIT 10;""",
            True,
        )
        return result

    def get_products_order_count_by_month(self):
        result = self.query(
            """SELECT
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN 1 ELSE 0 END) AS "Январь",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN 1 ELSE 0 END) AS "Февраль",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN 1 ELSE 0 END) AS "Март",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 4 THEN 1 ELSE 0 END) AS "Апрель",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 5 THEN 1 ELSE 0 END) AS "Май",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 6 THEN 1 ELSE 0 END) AS "Июнь",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 7 THEN 1 ELSE 0 END) AS "Июль",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 8 THEN 1 ELSE 0 END) AS "Август",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 9 THEN 1 ELSE 0 END) AS "Сентябрь",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 10 THEN 1 ELSE 0 END) AS "Октябрь",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 11 THEN 1 ELSE 0 END) AS "Ноябрь",
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 12 THEN 1 ELSE 0 END) AS "Декабрь"
    FROM order_products;""",
            True,
        )
        return result

    def get_exhibition_order_count_by_month(self):
        result = self.query(
            """SELECT
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 2 THEN 1 ELSE 0 END) AS "Февраль",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 1 THEN 1 ELSE 0 END) AS "Январь",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 4 THEN 1 ELSE 0 END) AS "Апрель",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 3 THEN 1 ELSE 0 END) AS "Март",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 5 THEN 1 ELSE 0 END) AS "Май",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 6 THEN 1 ELSE 0 END) AS "Июнь",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 7 THEN 1 ELSE 0 END) AS "Июль",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 8 THEN 1 ELSE 0 END) AS "Август",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 9 THEN 1 ELSE 0 END) AS "Сентябрь",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 10 THEN 1 ELSE 0 END) AS "Октябрь",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 11 THEN 1 ELSE 0 END) AS "Ноябрь",
    SUM(CASE WHEN EXTRACT(MONTH FROM book_date) = 12 THEN 1 ELSE 0 END) AS "Декабрь"
    FROM order_exhibition;""",
            True,
        )
        return result


if __name__ == "__main__":
    db = Database(
        db_name="flask_museum",
        user="artem",
        password="135246Art",
        host="34.118.21.179",
        port=5432,
    )
    print(db.all(table_name="user_user"))
