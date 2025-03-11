from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User
from db import db
import uuid
import hashlib
app = Flask(__name__)
app.secret_key = 'super secret key' #necessário colocar em um dotenv posteriormente
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

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
            return jsonify({'status': 'login.failed'})

        login_user(user)
        return jsonify({'status': 'login.success'})

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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
