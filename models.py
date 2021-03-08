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
    title = CharField(unique=True)
    entry_date = DateTimeField(default=datetime.date.today)
    time_spent = IntegerField(null=False)
    learned = TextField(null=False)
    resources = TextField(null=False)
    user = ForeignKeyField(User, backref='entries')

    class Meta:
        database = DATABASE

    def tagged_to_entry(self):
        return Entry.select().join(
            EntryTags, on='tag_id'
        ).where(journal_entry=self)


class Tag(BaseModel):
    content = CharField(max_length=55, null=False)
    tagged_entry = ForeignKeyField(Entry, backref="tags")


class EntryTags(Model):
    from_entry = ForeignKeyField(Entry, backref="relationships")
    to_entry = ForeignKeyField(Tag, backref="related_to")

    class Meta:
        database = DATABASE
        indexes = (
            (('from_entry', 'to_entry'), True),

        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables(
        [User, Entry, Tag, EntryTags],
        safe=True
    )
    DATABASE.close()
