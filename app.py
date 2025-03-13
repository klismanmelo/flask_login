from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User, Todo
from db import db
import uuid
import hashlib
import jwt
import datetime

app = Flask(__name__)
app.secret_key = 'super secret key' #necessário colocar em um dotenv posteriormente
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

def generate_token(user):
    """Gera um token JWT para o usuário autenticado."""
    payload = {
        "user_id": user.id,  # ID do usuário no banco de dados
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Expira em 2 horas
    }
    token = jwt.encode(payload, app.secret_key, algorithm="HS256")
    return token

@lm.user_loader
def load_user(id):
    user = db.session.query(User).filter_by(id=id).first()
    return user

@app.route('/')
@login_required
def index():
    print(current_user.username)
    return jsonify({'status': 'index.root'})

def password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return jsonify({'status': 'login.page'})
    elif request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password_form = data.get("password")
        user = db.session.query(User).filter_by(username=username, password=password_hash(password_form)).first()
        if not user:
            return jsonify({'status': 'login.failed'}), 401

        login_user(user)

        token = generate_token(user)
        return jsonify({'status': 'login.success', 'token': token})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return jsonify({'status': 'register.page'})
    elif request.method == "POST":
        data = request.get_json()
        id = str(uuid.uuid4())
        username = data.get("username")
        password_form = data.get("password")
        password = password_hash(password_form)
        new_user = User(id=id, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return jsonify({'status': 'created'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'logout'})

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if request.method == 'GET':
        user_todos = Todo.query.filter_by(user_id=current_user.id).all()

        # Convertendo objetos Todo para JSON
        todos_json = [
            {
                "description": todo.description,
                "completed": todo.completed
            }
            for todo in user_todos
        ]

        return jsonify({"todos": todos_json})
    elif request.method == 'POST':
        data = request.get_json()
        description = data.get('description')
        new_task = Todo(description=description, user_id=current_user.id)

        db.session.add(new_task)
        db.session.commit()

        if not new_task:
            return jsonify({'message': 'Erro ao adicionar tarefa'})

        return jsonify({'message': 'Tarefa adicionada com sucesso!'})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
