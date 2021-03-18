#!usr/bin/env python
import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

from peewee import *

DATABASE = SqliteDatabase('journal.db')


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    user_bio = CharField(max_length=1000)
    is_admin = BooleanField(default=False)

    @classmethod
    def create_user(cls, username, email, password, user_bio, is_admin=False):
        try:
            cls.create(
                username=username,
                email=email,
                password=generate_password_hash(password),
                user_bio=user_bio,
                is_admin=False
            )
        except IntegrityError:
            raise ValueError("User already exists!")


class Entry(Model):
    title = CharField(null=False)
    entry_date = DateTimeField(default=datetime.date.today)
    time_spent = IntegerField(null=False)
    learned = TextField(null=False)
    resources = TextField(null=False)
    user = ForeignKeyField(User)
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

    @classmethod
    def create_entry(cls,
                     title,
                     time_spent,
                     learned,
                     resources,
                     user,
                     ):
        try:
            cls.create(
                title=title,
                time_spent=time_spent,
                learned=learned,
                resources=resources,
                user=user,
            )
        except IntegrityError:
            raise ValueError("Please try again.")


class Tag(BaseModel):
    content = CharField()

    @classmethod
    def create_tags(cls, content):
        try:
            cls.create(
                content=content
            )
        except IntegrityError:
            raise ValueError("Please try again.")


class EntryTag(BaseModel):
    entry = ForeignKeyField(Entry)  # implied backref is entry
    tag = ForeignKeyField(Tag)  # implied backref is tag


def initialize():
    # EntryTag = Tag.entries.get_through_model()
    DATABASE.connect()
    DATABASE.create_tables(
        [User, Entry, Tag, EntryTag],
        safe=True
    )
    DATABASE.close()
