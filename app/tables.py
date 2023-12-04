from db import db


def get_last_users():
    result = db.query(
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


def get_products_order_count_by_month():
    result = db.query(
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


def get_exhibition_order_count_by_month():
    result = db.query(
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
