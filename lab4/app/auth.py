from functools import wraps
from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash
from faker import Faker
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from .repositories.user_repository import UserRepository
from app import db

user_repository = UserRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return User(user['id'], user['username'])
    return None


@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = request.form.get('remember_me', None) == 'on'

        user = user_repository.get_by_username_and_password(username, password)

        if user is not None:
            flash('Вы успешно аутентифицированы', 'success')
            login_user(User(user['id'], user['username']), remember=remember_me)
            next_url = request.args.get('next', url_for('index'))
            return redirect(next_url)
        
        flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.index'))
        
def check_for_login(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Вы не авторизованы')
            return redirect(url_for('index'))
        return function(*args, **kwargs)
    return wrapper
