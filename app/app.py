from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory,
    send_file,
)
from form import LoginForm, ProfileForm, RegistrationForm, ProductBuyForm
from flask_session import Session
from datetime import date, datetime
from db.db import Database
from tickets.ticket import create_tickets
from tickets.send import send_email, del_files
import os
from datetime import date, datetime
import ast
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config.from_pyfile("config.py")
Session(app)
database = Database(
    db_name="flask_museum",
    user="artem",
    password="135246Art",
    host="34.118.21.179",
    port=5432,
)


@app.route("/media/<path:filename>")
def media(filename):
    media_directory = "media/"  # Путь к директории с медиа-файлами
    return send_from_directory(media_directory, filename)


@app.route("/admin/download_json")
def download_json():
    return send_file("media/db/" + database.create_json(), as_attachment=True)


@app.route("/admin/download_pdf/<data>")
def download_pdf(data):
    data = ast.literal_eval(data)
    name = database.create_pdf(data)
    return send_file("media/pdf/" + name, as_attachment=True)


# MAIN CONTENT
@app.route("/")
def index():
    context = {"title": f"а"}
    return render_template("catalog/index.html", context=context)


@app.route("/about")
def about():
    context = {"title": "О нас"}
    return render_template("catalog/about.html", context=context)


@app.route("/contacts")
def contacts():
    context = {"title": "Контакты"}
    return render_template("catalog/contacts.html", context=context)


@app.route("/exhibitions")
def exhibitions():
    if session["is_superuser"]:
        context = {
            "title": "Выставки",
            "exhibitions": database.filter(
                table_name="catalog_exhibition", type_id=1
            ),
        }
    else:
        context = {
            "title": "Выставки",
            "exhibitions": database.query(
                "SELECT * FROM catalog_exhibition WHERE (type_id = 1) AND (CURRENT_DATE BETWEEN start_date AND end_date) AND (tickets_quantity > 0)",
                True,
            ),
        }
    return render_template("catalog/exhibition.html", context=context)


@app.route("/events")
def events():
    if session["is_superuser"]:
        context = {
            "title": "События",
            "events": database.filter(
                table_name="catalog_exhibition", type_id=2
            ),
        }
    else:
        context = {
            "title": "События",
            "events": database.query(
                "SELECT * FROM catalog_exhibition WHERE (type_id = 2) AND (CURRENT_DATE BETWEEN start_date AND end_date) AND (tickets_quantity > 0)",
                True,
            ),
        }
    return render_template("catalog/events.html", context=context)


@app.route("/change_exhibit_info/<int:id>", methods=["POST"])
def change_exhibit_info(id):
    uppload_file = request.files["img"]
    form = dict(request.form)
    if uppload_file.filename != "":
        os.remove(
            "media/"
            + database.get(table_name="catalog_exhibition", id=id, name="img")
        )
        filepath = "media/exhibition_images/"
        uppload_file.save(os.path.join(filepath, uppload_file.filename))
        form["img"] = "exhibition_images/" + uppload_file.filename

    database.update(
        table_name="catalog_exhibition", key="id", key_value=id, **form
    )
    return redirect(request.referrer)


@app.route("/delete_exhibit/<int:id>")
def delete_exhibit(id):
    database.delete(table_name="catalog_exhibition", condition=f"id = {id}")
    return redirect(request.referrer)


@app.route("/create_exhibit", methods=["POST"])
def create_exhibit():
    uppload_file = request.files["img"]
    form = dict(request.form)
    if uppload_file.filename != "":
        filepath = "media/exhibition_images"
        uppload_file.save(os.path.join(filepath, uppload_file.filename))
        form["img"] = "exhibition_images/" + uppload_file.filename
    else:
        form["img"] = ""
    database.create(table_name="catalog_exhibition", **form)
    return redirect(request.referrer)


# USER METHODS
@app.route("/user/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if not form.validate():
            print("Invalid login form")
        else:
            user = database.filter(
                table_name="user_user", username=form.data["username"]
            )[0]
            if user != []:
                # Checking password
                if pbkdf2_sha256.verify(
                    form.data["password"], user["password"]
                ):
                    session["logged_in"] = True
                    session["username"] = form.data["username"]
                    session["is_superuser"] = user["is_superuser"]
                    session["user_id"] = database.get_user_id(
                        table_name="user_user", username=form.data["username"]
                    )
                    database.last_login(
                        table_name="user_user", id=session["user_id"]
                    )
                    return redirect(url_for("index"))
                else:
                    return render_template(
                        "user/login.html",
                        form=form,
                        error="Неправильный пароль",
                    )
            else:
                return render_template(
                    "user/login.html",
                    form=form,
                    error="Нету такого пользователя",
                )
    else:
        return render_template("user/login.html", form=form)


@app.route("/user/registration", methods=["POST", "GET"])
def registration():
    form = RegistrationForm(request.form)
    if request.method == "POST":
        if not form.validate():
            return render_template(
                "user/registration.html",
                form=form,
                errors=[elem[0] for elem in form.errors.values()],
            )
        else:
            if database.exists("user_user", username=form.data["username"]):
                return render_template(
                    "user/registration.html",
                    form=form,
                    error="Существет пользователь с таким логином",
                )
            else:
                database.create(
                    table_name="user_user",
                    username=form.data["username"],
                    last_name=form.data["last_name"],
                    password=database.code(form.data["password1"]),
                    is_superuser=False,
                    date_joined=f"{datetime.now()}",
                    first_name=form.data["first_name"],
                    email=form.data["email"],
                )
                session["logged_in"] = True
                session["is_superuser"] = False
                session["username"] = form.data["username"]
                session["user_id"] = database.get_user_id(
                    "user_user", username=form.data["username"]
                )
                return redirect(url_for("index"))
    else:
        return render_template("user/registration.html", form=form)


@app.route("/upload/<int:user_id>", methods=["POST"])
def upload(user_id):
    user = database.filter(table_name="user_user", id=user_id)[0]
    uppload_file = request.files["file"]
    file_path = "media/users_images/"
    uppload_file.save(os.path.join(file_path, uppload_file.filename))
    if user["img"] != "":
        os.remove("media/" + user["img"])
    database.update(
        table_name="user_user",
        key="id",
        key_value=user["id"],
        img="users_images/" + uppload_file.filename,
    )
    return redirect(request.referrer)


@app.route("/user/profile", methods=["GET", "POST"])
def profile():
    form = ProfileForm(request.form)
    user = database.filter(
        table_name="user_user", username=session["username"]
    )[0]
    baskets = database.query(
        f"""SELECT cb.id, cb.quantity, ce.name,
                        ce.description, ce.price
                         FROM catalog_basket cb
                       JOIN catalog_exhibition ce
                        ON ce.id=cb.exhibition_id
                        WHERE cb.user_id = {user['id']}""",
        True,
    )
    total_count = sum([basket["quantity"] for basket in baskets])
    total_price = sum(
        [basket["quantity"] * basket["price"] for basket in baskets]
    )
    if request.method == "POST":
        changed_data = {
            "first_name": form.data["first_name"],
            "last_name": form.data["last_name"],
        }

        database.update(
            table_name="user_user",
            key="id",
            key_value=user["id"],
            **changed_data,
        )
        return redirect("profile")
    else:
        if session["is_superuser"]:
            first_table = database.get_last_users()
            second_table = database.get_products_order_count_by_month()
            third_table = database.get_exhibition_order_count_by_month()
            return render_template(
                "user/profile.html",
                form=form,
                title="Профиль",
                user=user,
                baskets=baskets,
                total_count=total_count,
                total_price=total_price,
                first_table=first_table,
                second_table=second_table,
                third_table=third_table,
            )
        else:
            return render_template(
                "user/profile.html",
                form=form,
                title="Профиль",
                user=user,
                baskets=baskets,
                total_count=total_count,
                total_price=total_price,
            )


@app.route("/admin/create_superuser", methods=["POST"])
def create_superuser():
    form = dict(request.form)
    print(form)
    form["password"] = database.code(form["password"])
    now = datetime.now()
    database.create(
        table_name="user_user",
        **form,
        is_superuser=True,
        img="",
        last_login=now,
        date_joined=now,
        email="uchebaivanovic@gmail.com",
    )
    return redirect(request.referrer)


@app.route("/user/logout")
def logout():
    print(session["username"])
    session["username"] = None
    session["is_superuser"] = None
    session["logged_in"] = False
    session["user_id"] = None
    return redirect(request.referrer)


@app.route("/user/basket_add/<int:exhibit_id>")
def basket_add(exhibit_id):
    if session["logged_in"]:
        exhibition = database.filter(
            table_name="catalog_exhibition", id=exhibit_id
        )[0]
        basket = database.filter(
            table_name="catalog_basket",
            user_id=session["user_id"],
            exhibition_id=exhibition["id"],
        )
        if basket == []:
            database.create(
                table_name="catalog_basket",
                quantity=1,
                exhibition_id=exhibition["id"],
                user_id=session["user_id"],
            )
        else:
            database.update(
                table_name="catalog_basket",
                key="id",
                key_value=basket[0]["id"],
                quantity=basket[0]["quantity"] + 1,
            )

        return redirect(request.referrer)
    else:
        return redirect(url_for("login"))


@app.route("/user/basket_delete/<int:basket_id>")
def delete_basket(basket_id):
    database.delete(table_name="catalog_basket", condition=f"id = {basket_id}")
    return redirect(request.referrer)


@app.route("/change_product_info/<int:id>", methods=["POST"])
def change_product_info(id):
    uppload_file = request.files["img"]
    form = dict(request.form)
    if uppload_file.filename != "":
        os.remove(
            "media/"
            + database.get(table_name="shop_product", id=id, name="img")
        )
        filepath = "media/product_images/"
        uppload_file.save(os.path.join(filepath, uppload_file.filename))
        form["img"] = "product_images/" + uppload_file.filename

    database.update(table_name="shop_product", key="id", key_value=id, **form)
    return redirect(request.referrer)


@app.route("/create_product_category", methods=["POST"])
def create_product_category():
    form = request.form
    database.create(table_name="shop_producttype", **form)
    return redirect(request.referrer)


@app.route("/delete_product_category", methods=["POST"])
def delete_product_category():
    id = request.form["id"]
    database.delete(table_name="shop_producttype", condition=f"id = {id}")
    return redirect(request.referrer)


@app.route("/delete_product/<int:id>")
def delete_product(id):
    database.delete(table_name="shop_product", condition=f"id = {id}")
    return redirect(request.referrer)


@app.route("/create_product", methods=["POST"])
def create_product():
    uppload_file = request.files["img"]
    form = dict(request.form)
    if uppload_file.filename != "":
        filepath = "media/product_images"
        uppload_file.save(os.path.join(filepath, uppload_file.filename))
        form["img"] = "product_images/" + uppload_file.filename
    else:
        form["img"] = ""
    database.create(table_name="shop_product", **form)
    return redirect(request.referrer)


@app.route("/shop")
def shop():
    categories = database.all(table_name="shop_producttype")
    form = request.args
    search_text = form.getlist("search_text")
    category_ids = form.getlist("category_ids")
    if form:
        query = "SELECT * FROM shop_product WHERE "
        conditions = []

        if search_text:
            conditions.append(f"name LIKE '%{search_text[0]}%'")

        if category_ids:
            if len(category_ids) == 1:
                conditions.append(f"category_id = {category_ids[0]}")
            else:
                category_ids = tuple(category_ids)
                conditions.append(f"category_id IN {category_ids}")

        if conditions:
            query += " AND ".join(conditions)
        products = database.query(query, True)
    else:
        products = database.all(table_name="shop_product")
    return render_template(
        "shop/shop.html",
        title=f"Магазин",
        categories=categories,
        products=products,
    )


@app.route("/shop/about")
def shop_about():
    return render_template("shop/about.html", title="О магазине")


@app.route("/shop/basket_add/<int:product_id>")
def basket_product_add(product_id):
    if not session["logged_in"]:
        return redirect(url_for("login"))
    product = database.filter(table_name="shop_product", id=product_id)[0]
    basket = database.filter(
        table_name="shop_basket",
        user_id=session["user_id"],
        product_id=product["id"],
    )
    if basket == []:
        database.create(
            table_name="shop_basket",
            quantity=1,
            product_id=product["id"],
            user_id=session["user_id"],
        )
    else:
        database.update(
            table_name="shop_basket",
            key="id",
            key_value=basket[0]["id"],
            quantity=basket[0]["quantity"] + 1,
        )

    return redirect(request.referrer)


@app.route("/shop/basket", methods=["GET", "POST"])
def shop_basket():
    if not session["logged_in"]:
        return redirect(url_for("login"))
    user = database.filter(
        table_name="user_user", username=session["username"]
    )[0]
    baskets = database.query(
        f"""SELECT sb.id, sb.quantity, sp.name, sp.description,
        sp.price FROM shop_basket
        sb JOIN shop_product sp
        ON sb.product_id=sp.id
        WHERE sb.user_id = {user['id']}""",
        True,
    )
    form = ProductBuyForm(request.form)
    total_count = sum([basket["quantity"] for basket in baskets])
    total_price = sum(
        [basket["quantity"] * basket["price"] for basket in baskets]
    )
    if request.method == "POST":
        for basket in baskets:
            database.insert(
                f"INSERT INTO order_products(user_id, product_id, quantity, order_date, delivery_date) VALUES ({user['id']}, {basket['id']}, {basket['quantity']}, '{(date.today())}',  '{form.data['take_date']}');"
            )
            database.delete(
                table_name="shop_basket", condition=f"id = {basket['id']}"
            )
        return redirect(url_for("shop_basket"))
    else:
        return render_template(
            "shop/basket.html",
            baskets=baskets,
            total_count=total_count,
            total_price=total_price,
            title="Корзина",
            form=form,
        )


@app.route("/shop/basket_delete/<int:basket_id>")
def basket_product_delete(basket_id):
    database.delete(table_name="shop_basket", condition=f"id = {basket_id}")
    return redirect(request.referrer)


@app.route("/user/checkout/<int:user_id>")
def checkout_exhbibition(user_id):
    """INSERT INTO order_exhibition(user_id,exhibition_id,quantity,book_date) VALUES(14,1,0,'2023-11-16');"""
    user = database.filter(table_name="user_user", id=user_id)[0]
    baskets = database.filter(table_name="catalog_basket", user_id=user["id"])
    for basket in baskets:
        if not database.exists(
            table_name="order_exhibition", exhibition_id=basket["exhibition_id"]
        ):
            query = f"""INSERT INTO order_exhibition(user_id, exhibition_id, quantity, book_date) VALUES({user['id']}, {basket['exhibition_id']},{basket['quantity']}, '{date.today()}')"""
            database.insert(query)
            print("\n" * 50)
        else:
            database.query(
                f"UPDATE order_exhibition SET quantity = quantity + {basket['quantity']} WHERE exhibition_id = {basket['exhibition_id']}"
            )
        database.query(
            f"UPDATE catalog_exhibition SET tickets_quantity = tickets_quantity - {basket['quantity']} WHERE id = {basket['exhibition_id']}"
        )
        database.delete(
            table_name="catalog_basket",
            condition=f"exhibition_id = {basket['exhibition_id']}",
        )
        # Create a ticket
        order = database.query(
            str(
                """SELECT oe.id, ce.name, ce.start_date, ce.end_date, oe.quantity,
                 (oe.quantity*ce.price) as total_price FROM order_exhibition as oe
                 JOIN catalog_exhibition as ce
                 ON ce.id = oe.exhibition_id;"""
            ),
            True,
        )[0]
        create_tickets(
            id=order["id"],
            name=order["name"],
            start_date=order["start_date"],
            end_date=order["end_date"],
            tickets_count=order["quantity"],
            total_price=order["total_price"],
        )
    # send email
    send_email(user["email"])
    # delete tickets
    del_files()
    return redirect(url_for("profile"))


@app.route("/user/forgot_password")
def forgot_password():
    ...


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
