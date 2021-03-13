#!usr/bin/env python
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField,
                     IntegerField)
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                Email, Length, EqualTo, Optional)

from models import User, Entry


def validate_title(field, form):
    if Entry.select().where(Entry.title == field.data).exists():
        raise ValidationError("There's already an entry with this title!")


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegistrationForm(FlaskForm):
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


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(FlaskForm):
    title = StringField('Title:', validators=[DataRequired(), validate_title])
    # date = DateField('Date of Study:', format='%d-%m-%Y')
    time_spent = IntegerField(
        "Study Time (Minutes):", validators=[DataRequired()]
    )
    learned = TextAreaField("What I Learned:", validators=[DataRequired()])
    resources = TextAreaField("Resources for further learning:",
                              validators=[Optional()])
    tag = StringField(
        'Subject Tags:',
        validators=[
            Optional(),
            Regexp(
                r'^[a-zA-Z0-9_\s]+$',
                message="Tags must best letters. "
                "Spaces separate individual tags."
            )
        ])
