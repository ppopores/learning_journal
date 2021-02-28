#!usr/bin/env python

from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'sadfjksdf9sadvcnasdfl0.14cv.asdf541asd.'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    reg_form = forms.RegistrationForm()
    if reg_form.validate_on_submit():
        flash("Successfully Registered!", "success")
        models.User.create_user(
            username=reg_form.username.data,
            email=reg_form.email.data,
            password=reg_form.password.data,
            user_bio=reg_form.user_bio.data
        )
        return redirect(url_for('index.html'))
    return render_template('registration.html', reg_form=reg_form)

# create index view, register view
# / - Known as the root page, homepage,
# landing page but will act as the Listing route.


@app.route('/login', methods=('GET', 'POST'))
def login():
    login_form = forms.LoginForm()
    if login_form.validate_on_submit():
        try:
            user = models.User.get(
                models.User.email == login_form.email.data
            )
        except models.DoesNotExist:
            flash("Hey there!"
                  "Looks like you've misspelled "
                  "either your email or password. "
                  "Or you aren't registered yet!",
                  "error"
                  )
        else:
            if check_password_hash(
                    user.password,
                    login_form.password.data
            ):
                login_user(user)
                flash("Success!!! All logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Hey there!"
                      "Looks like you've misspelled "
                      "either your email or password. "
                      "Or you aren't registered yet!",
                      "error"
                      )
    return render_template('login.html', login_form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))


@app.route('/entries/<int:entry_id>')
@login_required
def view_entries(entry_id):
    user_entries = models.Entry.select().where(
        models.Entry.id == entry_id
    )
    if user_entries.count() == 0:
        abort(404)
    return render_template('learn_journ.html', learn_journ=user_entries)


@app.route('/')
def index():
    # use playhouse.sqliteq to paginate results before finishing/del limit
    learn_journ = models.Entries.select().limit(100)
    return render_template('learn_journ.html', learn_journ=learn_journ)


# Create each of the following routes for your application

# /entries - Also will act as the Listing route just like /

# /entries/new - The Create route
# @app.route('/entries/new')
# # /entries/<id> - The Detail route
# @ap.route('/entries/<entry_id>')
# # /entries/<id>/edit - The Edit or Update route
# @app.route('/entries/<entry_id>/edit')
# # /entries/<id>/delete - Delete route
# @app.route('entries/<entry_id>/delete')
if __name__ == '__main__':
    models.initialize()
    # models.User.create_user(
    #     username='ppopores',
    #     email='ppopores@gmail.com',
    #     password='treehouse',
    #     user_bio='student',
    #     is_admin=True
    # )
    app.run(debug=DEBUG, host=HOST, port=PORT)
