from flask import Flask, render_template, request, redirect, url_for, session
from db.db import Database
from form import LoginForm, ProfileForm, RegistrationForm
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
                db.last_login(table_name='user_user', username=session['username'])
                return redirect(url_for('index'))
            else:
                return render_template("user/login.html", form=form, error='Неправильный логин или пароль')
    else:
        return render_template("user/login.html", form=form)

@app.route("/user/registration", methods=["POST", "GET"])
def registration():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        if not form.validate():
            return render_template("user/registration.html", form=form, errors=[elem[0] for elem in form.errors.values()])
        else:
            if db.exists('user_user', username=form.data['username']):
                return render_template("user/registration.html", form=form, error='Существет пользователь с таким логином')
            else:
                db.create(table_name='user_user', username =form.data['username'], last_name=form.data['last_name'],
                        password=form.data['password1'], first_name=form.data['first_name'],
                        email=form.data['email'])
                session['logged_in'] = True
                session['username'] = form.data['username']
                return redirect(url_for('index'))
    else:
        return render_template("user/registration.html", form=form)

@app.route("/user/profile", methods=['GET', 'POST'])
def profile():
    form = ProfileForm(request.form)
    user = db.filter(table_name='user_user', username=session['username'])[0]
    if request.method == 'POST':
        uppload_file = request.files['img']
        if uppload_file.filename != '':
            file_path = 'app/static/media/users_images/' + uppload_file.filename
            uppload_file.save(file_path)
            changed_data = {
                'first_name': form.data['first_name'],
                'last_name': form.data['last_name'],
                'img': 'users_images/' + uppload_file.filename
            }
        else:
            changed_data = {
                'first_name': form.data['first_name'],
                'last_name': form.data['last_name'],
            }
        
        db.update(table_name='user_user', key='id', key_value=user['id'], **changed_data)
        return redirect('profile') 
    else:
        return render_template("user/profile.html", form=form,
                            title='Профиль', user=user)  

@app.route('/user/logout')
def logout():
    print(session['username'])
    session['username'] = None
    session['logged_in'] = False
    return redirect(url_for('index'))



