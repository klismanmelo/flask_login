from db import db
from flask_login import UserMixin
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))