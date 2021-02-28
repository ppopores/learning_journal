from flask_wtf import Form
from wtforms import (StringField, PasswordField, TextAreaField,
                     IntegerField, DateField)
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Email, Length, EqualTo, Optional)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegistrationForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message='Passwords must match!')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )
    user_bio = TextAreaField(
        'Short Bio',
        validators=[
            Optional(),
            Length(max=1000)
        ])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(Form):
    title = StringField('Title:', validators=[DataRequired()])
    date = DateField('Date of Study:', format='%Y-%m-%d')
    time_spent = IntegerField(
        "Study Time (Minutes):", validators=[DataRequired()]
    )
    learned = TextAreaField("What I Learned:", validators=[DataRequired()])
    resources = TextAreaField("Resources for further learning:",
                              validators=[Optional()])
