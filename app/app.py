from flask import Flask, render_template, request, redirect, url_for, session
from db.db import Database
from form import LoginForm
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY very long"
app.config['SESSION_TYPE'] = 'filesystem'
db = Database(db_name="flask_museum", user="admin", password="root") 
Session(app)

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
        'exhibitions': db.filter(table_name='catalog_exhibition', type_id=1)
    }
    return render_template("catalog/exhibition.html", context=context)

@app.route("/events")
def events():
    context = {
        'title': 'Выставки',
        'events': db.filter(table_name='catalog_exhibition', type_id=2)
    }
    return render_template("catalog/events.html", context=context)


@app.route("/user/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            print('Invalid login form')
        else:
            if db.exists('user_user', username=form.data['username'], password=form.data['password']):
                session['logged_in'] = True
                session['username'] = form.data['username']
                return redirect(url_for('index'))
            else:
                return render_template("user/login.html", form=form, error='Неправильный логин или пароль')
    else:
        return render_template("user/login.html", form=form)

@app.route("/user/registration")
def registration():
    ...

@app.route("/user/profile")
def profile():
    context = {
        'title': 'Профиль',
        'user': db.filter(table_name='user_user', username=str(session['username']))
    }
    return render_template("user/profile.html", context=context)  

@app.route('/user/logout')
def logout():
    session['username'] = None
    session['logged_in'] = False
    return redirect(url_for('index'))



