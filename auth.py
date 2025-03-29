import models as db
import jwt
import datetime
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, request, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine, String, Integer, Column, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from flask_sqlalchemy import SQLAlchemy
SECRET_KEY = "secret_key1234"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/database' # это поменяй
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
class BlogPost:
    __tablename__ = 'blog_posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="blog_posts")
with app.app_context():
    db.create_all()
async def password_auth(user: db.User, password: str):
    if user and check_password_hash(user.password_hash, password):
        return True
    else:
        return False
async def generate_token(user: db.User):
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
async def token_auth(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        with app.app_context():
            user = db.session.get(db.User, user_id)
        if user:
            return user
        else:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Токен отсутствует'}), 401
        user = await token_auth(token)
        if not user:
            return jsonify({'message': 'Недействительный токен'}), 401
        return await f(user, *args, **kwargs)
    return decorated
@app.route('/login', methods=['POST'])
async def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'message': 'Необходимо предоставить имя пользователя и пароль'}), 400
    with app.app_context():
        user = db.User.query.filter_by(username=username).first()
        if user and password_auth(user, password):
            token = await generate_token(user)
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Неверные учетные данные'}), 401
@app.route('/protected', methods=['GET'])
@token_required
async def protected(user):
    return jsonify({'message': f'Привет, {user.username}! Это защищенный маршрут.'}), 200
@app.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        car_number = request.form.get('car_number', '')
        phone_number = request.form.get('phone_number', '')
        with app.app_context():
            existing_user = db.User.query.filter_by(username=username).first()
            if existing_user:
                return render_template('register.html', error='Пользователь с таким именем уже существует')
            new_user = db.User(username=username, car_number=car_number, phone_number=phone_number)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')