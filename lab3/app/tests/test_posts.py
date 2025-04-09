import pytest
from app import app, posts_list
from flask import template_rendered, session
from contextlib import contextmanager
from datetime import timedelta

def get_users():
    return [
        {
            'id':'1',
            'login': 'user',
            'password': 'qwerty'
        }
    ]


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

# --------------- Счетчик ---------------------------------------------------------
def test_counter_increment(client):
    rv = client.get('/counter')
    assert 'Вы посетили эту страницу 1' in rv.data.decode('utf-8')
    rv = client.get('/counter')
    assert 'Вы посетили эту страницу 2' in rv.data.decode('utf-8')

def test_counter_isolated_sessions():
    app.config['TESTING'] = True
    with app.test_client() as c1:
        rv1 = c1.get('/counter')
        assert 'Вы посетили эту страницу 1' in rv1.data.decode('utf-8')
        rv1 = c1.get('/counter')
        assert 'Вы посетили эту страницу 2' in rv1.data.decode('utf-8')

    with app.test_client() as c2:
        rv2 = c2.get('/counter')
        assert 'Вы посетили эту страницу 1' in rv2.data.decode('utf-8')

# ---------------- Успешная аутентификация ------------------------------
 
def test_successful_message(client):
    response = client.post('/auth', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'on'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Вы успешно аунтефицированы' in response.data.decode('utf-8')

# ------------ Неспешная аутентификация -----------------------------

def test_failed_message(client):
    response = client.post('/auth', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })

    assert response.status_code == 200
    assert 'Пользователь не найден' in response.data.decode('utf-8')

# ------------Успешно Секретная страница -------------------------------------

def test_saccess_secret_page(client):
    response = client.post('/auth', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)

    assert 'Вы успешно аунтефицированы' in response.data.decode('utf-8')

    secret_response = client.get('/secret')
    assert secret_response.status_code == 200
    assert 'Секрет' in secret_response.data.decode('utf-8')

# ------------Не Успешно Секретная страница -------------------------------------

def test_fall_secret_page(client):
    response = client.get('/secret', follow_redirects=True)
    assert 'Необходимо авторизоваться' in response.data.decode('utf-8')
    assert 'Регистрация' in response.data.decode('utf-8')

# ------------Успешный переход после авторизации -------------------------------------

def test_to_secret_page(client):
    rv = client.post('/auth', data=dict(
        username='user', 
        password='qwerty', 
        remember_me='on'
    ), follow_redirects=True)
    
    rv = client.get('/secret', follow_redirects=True)
    
    assert rv.status_code == 200

# -------------- remember_token ---------------------------------------------

def test_remember_me_functionality(client):
    user = get_users()[0]
    response = client.post('/login', data={
        'username': user['login'],
        'password': user['password'],
        'remember_me': 'on'
    })
    assert 'remember_token' in response.headers.get('Set-Cookie', '')


# -------------------- navbar --------------------

def test_navbar_authenticated(client):
    response = client.post('/auth', data=dict(
        username='user', 
        password='qwerty', 
        remember_me='on'
    ), follow_redirects=True)
    
    response = client.get('/', follow_redirects=True)
        
    assert 'Секрет' in response.data.decode('utf-8')
    assert 'Выйти' in response.data.decode('utf-8')

# Тест для неаутентифицированного пользователя
def test_navbar_not_authenticated(client):
    response = client.get('/', follow_redirects=True)
        
    assert 'Войти' in response.data.decode('utf-8')