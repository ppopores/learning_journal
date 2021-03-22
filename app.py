#!usr/bin/env python
from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from datetime import datetime

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
    tag_form = forms.TagForm()
    if entry_form.validate_on_submit():
        models.Entry.create_entry(
            user=g.user.id,
            title=entry_form.title.data,
            time_spent=entry_form.time_spent.data,
            learned=entry_form.learned.data,
            resources=entry_form.resources.data,
        )
        try:
            if tag_form.validate_on_submit():
                tags = tag_form.tag_content.data.split()
                for tag in tags:
                    models.Tag.create_tags(tag)
                    models.EntryTag.create_linked_tag(
                        entry=entry_form.title.data,
                        tag=tag
                    )
        except IntegrityError:
            pass
        flash("Rad! New entry submitted!", "success")
        return redirect(url_for('index'))
    return render_template(
        "new.html", entry_form=entry_form, tag_form=tag_form)


@app.route('/entries/<int:entry_id>')
@login_required
def detail(entry_id):
    try:
        entry = models.Entry.get(
            models.Entry.id == entry_id
        )
        entry_tags = models.Tag.get_entry_tags(entry_id)
        return render_template(
            'detail.html',
            entry=entry,
            entry_tags=entry_tags
        )
    except models.DoesNotExist:
        abort(404)


@ app.route('/tags/<int:tag_id>')
@ login_required
def tags(tag_id):
    try:
        tagged_entries = (models.Entry
                          .select()
                          .join(models.EntryTag)
                          .join(models.Tag)
                          .where(tag_id == models.EntryTag.id)
                          )
        specific_tag = (models.Tag.get(tag_id == models.Tag.id))

        return render_template("tags.html",
                               tagged_entries=tagged_entries,
                               specific_tag=specific_tag)
    except models.DoesNotExist:
        abort(404)


@ app.route('/')
@ login_required
def index():
    entries = (models.Entry
               .select()
               .join(models.EntryTag)
               .join(models.Tag)
               )
    specific_tag = (models.Tag.get(entries.tag_id == models.Tag.id))
    return render_template(
        'index.html',
        entries=entries,
        specific_tag=specific_tag
    )


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
    try:
        current_entry = models.Entry.get(
            entry_id == models.Entry.id
        )
        if g.user.id is current_entry.user_id:
            form = forms.EntryForm(obj=current_entry)
            if form.validate_on_submit():
                edited_entry = models.Entry.update(
                    user=g.user.id,
                    # title=form.title.data,
                    time_spent=form.time_spent.data,
                    learned=form.learned.data,
                    resources=form.resources.data,
                    # tag=form.tag.data
                )
                edited_entry.execute()
                flash("Edited and updated!", "success")
                return redirect(url_for('index'))
            else:
                return render_template(
                    'edit.html', current_entry=current_entry, form=form
                )
        else:
            flash("Hey! This isn't yours to edit!", "error")
            return redirect(url_for('index'))
    except models.EntryDoesNotExist:
        abort(404)


@ app.route('/entries/<int:entry_id>/delete', methods=('GET', 'POST'))
@ login_required
def delete_entry(entry_id):
    try:
        current_entry = models.Entry.get(
            entry_id == models.Entry.id
        )
        if g.user.id is current_entry.user_id:
            models.Entry.delete_instance(current_entry)
            flash("Entry deleted forever!", "success")
            return redirect(url_for('index'))
        else:
            flash("Can't delete that which you did not create.", "error")
            return redirect(url_for('index'))
        return render_template(
            'delete.html', current_entry=current_entry)
    except models.DoesNotExist:
        abort(404)


@ app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
    app.run(debug=True)
