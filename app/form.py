from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    EmailField,
    validators,
    FileField,
    DateField,
    RadioField,
)
from datetime import date, timedelta


class LoginForm(FlaskForm):
    username = StringField(
        "Имя пользователя", [validators.Length(min=2, max=256)]
    )
    password = PasswordField(
        "Пароль",
        [
            validators.DataRequired(),
        ],
    )


class ProfileForm(FlaskForm):
    first_name = StringField("Имя")
    last_name = StringField("Фамилия")
    username = StringField("Логин", [validators.Length(min=4)])
    email = EmailField(
        "Email",
        [
            validators.Regexp(
                "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+",
                message="Invalid email address",
            )
        ],
    )
    password = StringField("Пароль")


class RegistrationForm(FlaskForm):
    first_name = StringField("Имя", [validators.DataRequired()])
    last_name = StringField("Фамилия", [validators.DataRequired()])
    username = StringField(
        "Логин", [validators.Length(min=4), validators.DataRequired()]
    )
    email = StringField(
        "Email",
        [
            validators.Regexp(
                "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+",
                message="Invalid email address",
            )
        ],
    )
    password1 = PasswordField("Пароль", [validators.DataRequired()])
    password2 = PasswordField(
        "Повторите пароль",
        [
            validators.DataRequired(),
            validators.EqualTo("password1", "Пароли должны быть одинаковы"),
        ],
    )


class ProductBuyForm(FlaskForm):
    take_date = DateField(
        "Дата доставки",
        validators=[validators.DataRequired()],
        default=date.today() + timedelta(days=4),
        render_kw={"disabled": True},
    )
    payment_type = RadioField(
        "Способ оплаты",
        choices=[("card", "Картой"), ("cash", "Наличные")],
        validators=[validators.DataRequired()],
    )
