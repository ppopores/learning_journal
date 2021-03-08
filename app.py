#!usr/bin/env python

from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import forms
import models

from peewee import *

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
        return redirect(url_for('index'))
    return render_template('register.html', reg_form=reg_form)

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


@app.route('/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    entry_form = forms.EntryForm()
    tagging_form = forms.TaggingForm()
    if entry_form.validate_on_submit():
        try:
            models.Entry.create(
                user=g.user.id,
                title=entry_form.title.data,
                time_spent=entry_form.time_spent.data,
                learned=entry_form.learned.data,
                resources=entry_form.resources.data,
            )
            flash("Rad! New entry submitted!", "success")
        except IntegrityError:
            flash("Choose a unique title for each entry!")
        if tagging_form.data:
            try:
                with models.DATABASE.atomic():
                    models.Tag.create(content=tagging_form.content.data)
                    models.EntryTags.create(
                        entry=models.Entry.id,
                        tag=models.Tag.id
                    )
            except models.IntegrityError:
                pass
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    return render_template(
        "new.html", entry_form=entry_form, tagging_form=tagging_form)


# @app.route('/tag/<int:entry_id>')
# @login_required
# def tag_entry(entry_id):
#     try:
#         to_entry = models.Entry.get(models.Entry.entry_id**entry_id)
#     except models.DoesNotExist:
#         pass
#     else:
#         try:
#             models.EntryTags.create(
#                 entry=entry_id,
#                 tag=
#             )
#

@ app.route('/entries/<int:entry_id>')
@ login_required
def detail(entry_id):
    entry = models.Entry.get(
        models.Entry.id == entry_id
    )
    tags = (
        Tag.select()
        .join(EntryTags)
        .join(Tag)
        .where(
            (EntryTags.tag << tags) &
            (Entry.published is True)
        )
    )
    return render_template('detail.html', entry=entry, tags=tags)


@ app.route('/')
@ login_required
def index():
    entries = models.Entry.select().limit(100)
    return render_template('index.html', entries=entries)


@ app.route('/entries')
@ login_required
def entries():
    entries = models.Entry.select().where(
        g.user.id == models.Entry.user
    ).limit(100)
    return render_template('entries.html', entries=entries)


@ app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
@ login_required
def edit_entries(entry_id):
    current_entry = models.Entry.get(
        entry_id == models.Entry.id
    )
    if current_entry:
        form = forms.EntryForm(obj=current_entry)
        if form.validate_on_submit():
            edited_entry = models.Entry.update(
                user=g.user.id,
                # title=form.title.data,
                time_spent=form.time_spent.data,
                learned=form.learned.data,
                resources=form.resources.data,
            )
            edited_entry.execute()
            flash("Edited and updated!", "success")
            return redirect(url_for('index'))
        else:
            return render_template(
                'edit.html', current_entry=current_entry, form=form
            )
    else:
        pass


@ app.route('/entries/<int:entry_id>/delete', methods=('GET', 'POST'))
@ login_required
def delete_entry(entry_id):
    current_entry = models.Entry.get(
        entry_id == models.Entry.id
    )
    if current_entry:
        models.Entry.delete_instance(current_entry)
        flash("Entry deleted forever!", "success")
        return redirect(url_for('index'))
    else:
        return render_template(
            'delete.html', current_entry=current_entry)


# @app.route('/entries/<int:entry_id>/tag_entry')
# @login_required
# def tag_entry(entry_id):
#     try:
#         tagged_entry = models.Entry.get(models.Entry.entry_id**entry_id)
#     except models.DoesNotExist:
#         abort(404)
#     else:
#         try:
#             models.TagRelationship.create(
#                 created_by=g.Tag._get_current_object(),
#                 tag=form.a_tag.data,
#
#             )
#         except models.IntegrityError:
#             pass
#         else:
#             flash(f"You've tagged {tagged_entry.title}!", "success")
#     return redirect(url_for('index'))

if __name__ == '__main__':
    models.initialize()
    try:
        with models.DATABASE.transaction():
            models.User.create_user(
                username='ppopores',
                email='ppopores@gmail.com',
                password='treehouse',
                user_bio='student',
                is_admin=True
            )
    except ValueError:
        pass
    app.run()
