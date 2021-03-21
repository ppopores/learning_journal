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
            with DATABASE.transaction():
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
        # try:
        cls.create(
            title=title,
            time_spent=time_spent,
            learned=learned,
            resources=resources,
            user=user,
        )

    def get_tags():
        return(Tag
               .select(Entry, Tag, EntryTag)
               .join(Entry)
               .switch(EntryTag)
               .join(Tag)
               )


class Tag(BaseModel):
    tag_content = CharField(unique=True, null=False)

    @classmethod
    def create_tags(cls, tag_content):
        try:
            cls.create(
                tag_content=tag_content
            )
        except IntegrityError:
            pass

    @classmethod
    def find_entries(cls):
        return(Entry
               .select()
               .join(
                   EntryTag,
                   on=EntryTag.tag_entry
               ).where(
                   EntryTag.entry_tag == cls)
               )


class EntryTag(BaseModel):
    entry_tag = ForeignKeyField(Entry, backref='entry_tag')
    tag_entry = ForeignKeyField(Tag, backref='tag_entry')

    @classmethod
    def create_linked_tag(cls, entry, tag):
        tag = Tag.get(Tag.tag_content == tag)
        entry = Entry.get(Entry.title == entry)
        cls.create(
            tag_entry=tag.id,
            entry_tag=entry.id
        )


def initialize():
    # EntryTag = Tag.entries.get_through_model()
    DATABASE.connect()
    DATABASE.create_tables(
        [User, Entry, Tag, EntryTag],
        safe=True
    )
    DATABASE.close()
