from flask import Flask, render_template
from db.db import Database
app = Flask(__name__)


@app.route("/")
def index():
    context = {"title": "Главная"}
    return render_template("catalog/index.html", context=context)

@app.route("/about")
def about():
    context = {
        'title': "О нас"
    }
    return render_template("catalog/about.html", context=context)

@app.route("/contacts")
def contacts():
    context = {
        'title': "Контакты"
    }
    return render_template("catalog/contacts.html", context=context)

@app.route("/exhibitions")
def exhibitions():
    context = {
        'title': 'Выставки',
        'exhibitions': db.filter('catalog_exhibition', 'type_id=1')
    }
    return render_template("catalog/exhibition.html", context=context)

@app.route("/events")
def events():
    context = {
        'title': 'Выставки',
        'events': db.filter('catalog_exhibition', 'type_id=2')
    }
    return render_template("catalog/events.html", context=context)



if __name__ == "__main__":
    db = Database(db_name="flask_museum", user="admin", password="root")
    app.run(debug=True)
