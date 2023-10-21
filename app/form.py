from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, validators, IntegerField

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', [validators.Length(min=4, max=256)])
    password = PasswordField('Пароль', [
        validators.DataRequired(),
    ])

