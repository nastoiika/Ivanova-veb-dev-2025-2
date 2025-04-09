import random
from ssl import SSLSession
from flask import Flask, flash, render_template, abort, request, make_response, session, redirect, url_for
from faker import Faker
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import re

fake = Faker()

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'

def get_users():
    return [
        {
            'id':'1',
            'login': 'user',
            'password': 'qwerty'
        }
    ]

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if user_id == user['id']:
            return User(user['id'], user['login'])
    return None

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)
comments_list = generate_comments()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>')
def post(index):
    if index < 0 or index >= len(posts_list):
        abort(404)
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p, comments=comments_list)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/counter')
def counter():
    if session.get("counter"):
        session['counter'] += 1
    else:
        session['counter'] = 1
    return render_template('counter.html')

@app.route('/auth', methods=["GET","POST"])
def auth():
    next_page = request.args.get('next')
    if request.method == "POST":
        login = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        if login and password:
            for user in get_users():
                if user['login'] == login and user['password'] == password:
                    user = User(user['id'], user['login'])
                    login_user(user, remember=remember_me)
                    flash('Вы успешно аунтефицированы', 'success')
                    return  redirect(next_page or url_for('index'))
                
            return render_template('auth.html', title='Регистрация', error='Пользователь не найден')

    return render_template('auth.html', title='Регистрация')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html', title='Секрет')

if __name__ == '__main__':
    app.run(debug=True)
