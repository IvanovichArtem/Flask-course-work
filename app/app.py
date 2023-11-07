from flask import Flask, render_template, request, redirect, url_for, session
from db.db import Database
from form import LoginForm, ProfileForm, RegistrationForm
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET_KEY very long"
app.config["SESSION_TYPE"] = "filesystem"
db = Database(db_name="flask_museum", user="admin", password="root")
Session(app)


# MAIN CONTENT
@app.route("/")
def index():
    context = {"title": "Главная"}
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
    context = {
        "title": "Выставки",
        "exhibitions": db.query(
            "SELECT * FROM catalog_exhibition WHERE type_id = 1 AND CURRENT_DATE BETWEEN start_date AND end_date"
        ),
    }
    return render_template("catalog/exhibition.html", context=context)


@app.route("/events")
def events():
    context = {
        "title": "Выставки",
        "events": db.query(
            "SELECT * FROM catalog_exhibition WHERE type_id = 2 AND CURRENT_DATE BETWEEN start_date AND end_date"
        ),
    }
    return render_template("catalog/events.html", context=context)


# USER METHODS
@app.route("/user/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if not form.validate():
            print("Invalid login form")
        else:
            if db.exists(
                "user_user",
                username=form.data["username"],
                password=form.data["password"],
            ):
                session["logged_in"] = True
                session["username"] = form.data["username"]
                session["user_id"] = db.get_user_id(
                    "user_user", username=form.data["username"]
                )
                return redirect(url_for("index"))
            else:
                return render_template(
                    "user/login.html", form=form, error="Неправильный логин или пароль"
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
            if db.exists("user_user", username=form.data["username"]):
                return render_template(
                    "user/registration.html",
                    form=form,
                    error="Существет пользователь с таким логином",
                )
            else:
                db.create(
                    table_name="user_user",
                    username=form.data["username"],
                    last_name=form.data["last_name"],
                    password=form.data["password1"],
                    first_name=form.data["first_name"],
                    email=form.data["email"],
                )
                session["logged_in"] = True
                session["username"] = form.data["username"]
                session["user_id"] = db.get_user_id(
                    "user_user", username=form.data["username"]
                )
                return redirect(url_for("index"))
    else:
        return render_template("user/registration.html", form=form)


@app.route("/user/profile", methods=["GET", "POST"])
def profile():
    form = ProfileForm(request.form)
    user = db.filter(table_name="user_user", username=session["username"])[0]
    baskets = db.query(
        f"""SELECT cb.id, cb.quantity, ce.name,
                        ce.description, ce.price
                         FROM catalog_basket cb 
                       JOIN catalog_exhibition ce
                        ON ce.id=cb.exhibition_id
                        WHERE cb.user_id = {user['id']}"""
    )
    total_count = sum([basket["quantity"] for basket in baskets])
    total_price = sum([basket["quantity"] * basket["price"] for basket in baskets])
    if request.method == "POST":
        uppload_file = request.files["img"]
        if uppload_file.filename != "":
            file_path = "app/static/media/users_images/" + uppload_file.filename
            uppload_file.save(file_path)
            changed_data = {
                "first_name": form.data["first_name"],
                "last_name": form.data["last_name"],
                "img": "users_images/" + uppload_file.filename,
            }
        else:
            changed_data = {
                "first_name": form.data["first_name"],
                "last_name": form.data["last_name"],
            }

        db.update(
            table_name="user_user", key="id", key_value=user["id"], **changed_data
        )
        return redirect("profile")
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


@app.route("/user/logout")
def logout():
    print(session["username"])
    session["username"] = None
    session["logged_in"] = False
    session["user_id"] = None
    return redirect(url_for("index"))


@app.route("/user/basket_add/<int:exhibit_id>")
def basket_add(exhibit_id):
    if session["logged_in"]:
        exhibition = db.filter(table_name="catalog_exhibition", id=exhibit_id)[0]
        basket = db.filter(
            table_name="catalog_basket",
            user_id=session["user_id"],
            exhibition_id=exhibition["id"],
        )
        if basket == []:
            db.create(
                table_name="catalog_basket",
                quantity=1,
                exhibition_id=exhibition["id"],
                user_id=session["user_id"],
            )
        else:
            db.update(
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
    db.delete(table_name="catalog_basket", condition=f"id = {basket_id}")
    return redirect(request.referrer)


@app.route("/shop", defaults={"category_id": None})
@app.route("/shop/<int:category_id>")
def shop(category_id):
    categories = db.all(table_name="shop_producttype")
    if category_id:
        products = db.filter(table_name="shop_product", category_id=category_id)
    else:
        products = db.all(table_name="shop_product")
    return render_template(
        "shop/shop.html", title="Магазин", categories=categories, products=products
    )


@app.route("/shop/about")
def shop_about():
    return render_template("shop/about.html", title="О магазине")


@app.route("/shop/basket_add/<int:product_id>")
def basket_product_add(product_id):
    if not session["logged_in"]:
        return redirect(url_for("login"))
    product = db.filter(table_name="shop_product", id=product_id)[0]
    basket = db.filter(
        table_name="shop_basket",
        user_id=session["user_id"],
        product_id=product["id"],
    )
    if basket == []:
        db.create(
            table_name="shop_basket",
            quantity=1,
            product_id=product["id"],
            user_id=session["user_id"],
        )
    else:
        db.update(
            table_name="shop_basket",
            key="id",
            key_value=basket[0]["id"],
            quantity=basket[0]["quantity"] + 1,
        )

    return redirect(request.referrer)


@app.route("/shop/basket")
def shop_basket():
    if not session["logged_in"]:
        return redirect(url_for("login"))
    user = db.filter(table_name="user_user", username=session["username"])[0]
    baskets = db.query(
        f"""SELECT sb.id, sb.quantity, sp.name, sp.description,
        sp.price FROM shop_basket
        sb JOIN shop_product sp 
        ON sb.product_id=sp.id 
        WHERE sb.user_id = {user['id']}"""
    )
    total_count = sum([basket["quantity"] for basket in baskets])
    total_price = sum([basket["quantity"] * basket["price"] for basket in baskets])
    return render_template(
        "shop/basket.html",
        baskets=baskets,
        total_count=total_count,
        total_price=total_price,
        title="Корзина",
    )


@app.route("/shop/basket_delete/<int:basket_id>")
def basket_product_delete(basket_id):
    db.delete(table_name="shop_basket", condition=f"id = {basket_id}")
    return redirect(request.referrer)
