from flask import Flask, render_template

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
    ...


if __name__ == "__main__":
    app.run(debug=True)
