from db import db
from flask_login import UserMixin
from uuid import uuid4

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))

class Todo(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    description = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    #Chave Estrangeira: Relacionando a tarefa a um usuário
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)