import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    user_bio = CharField(max_length=1000)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('username',)

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
    # title
    title = CharField(unique=True)
    # entry date
    entry_date = DateField(default=datetime.date.today)
    # time spent
    time_spent = IntegerField(null=False)
    # learned
    learned = TextField(null=False)
    # resources
    resources = TextField(null=False)
    # user
    user = ForeignKeyField(
        model=User,
        backref='entries'
    )

    class Meta:
        database = DATABASE
    #    order_by = ('-entry_date',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()
