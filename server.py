from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='publik')  # Menentukan folder publik
app.secret_key = 'your_secret_key'  # Ganti dengan kunci yang lebih aman
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wuzanstore.db'  # Menggunakan database SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

# Model untuk pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Inisialisasi database
with app.app_context():
    db.create_all()

# Route untuk login page
@app.route('/login')
def login_page():
    return send_from_directory(os.path.join(app.root_path, 'publik'), 'login.html')

# Route untuk register page
@app.route('/register')
def register_page():
    return send_from_directory(os.path.join(app.root_path, 'publik'), 'register.html')

# Route untuk index page (Webstore page)
@app.route('/')
def index_page():
    return send_from_directory(os.path.join(app.root_path, 'publik'), 'index.html')

# Route Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('username')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email sudah digunakan!"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil! Silakan login."}), 200

# Route Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Email atau password salah!"}), 401

    session['user_id'] = user.id
    return jsonify({"message": "Login berhasil!"}), 200

# Route Webstore
@app.route('/webstore', methods=['GET'])
def webstore():
    if 'user_id' not in session:
        return jsonify({"message": "Harus login terlebih dahulu!"}), 401
    return redirect(url_for('index_page'))

# Route Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout berhasil!"}), 200

if __name__ == '__main__':
    app.run(debug=True)

