import pytest
from app import app, posts_list
from flask import template_rendered
from contextlib import contextmanager

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

def test_invalid_characters(client):
    rv = client.post('/number', data={'number': '123abc456'})
    content = rv.data.decode('utf-8')  
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in content
    assert 'is-invalid' in content

def test_invalid_number_length(client):
    rv = client.post('/number', data={'number': '12345'})
    content = rv.data.decode('utf-8')
    assert 'Неверное количество цифр' in content
    assert 'is-invalid' in content

def test_valid_number_formatting(client):
    rv = client.post('/number', data={'number': '+7 (999) 123-45-67'})
    content = rv.data.decode('utf-8')
    assert 'Номер: 89991234567' in content

@pytest.mark.parametrize("input_number, expected_output", [
    ("+7 (999) 123-45-67", "Номер: 89991234567"),
    ("8(999)1234567", "Номер: 89991234567"),
    ("9991234567", "Номер: 89991234567"),
    ("abcdefghijk", "В номере телефона встречаются недопустимые символы."),
    ("12345", "Неверное количество цифр"),
    ("+7 999 123 45 678", "Неверное количество цифр"),
    ("+7 999-123-45-67abc", "В номере телефона встречаются недопустимые символы."),
])
def test_number_validation(client, input_number, expected_output):
    rv = client.post('/number', data={'number': input_number})
    content = rv.data.decode('utf-8')
    assert expected_output in content

# ----------------- cookie -----------------------------

def test_cookies_set_and_delete(client):
    rv = client.get('/cookies')
    assert 'Set-Cookie' in rv.headers
    assert 'fio=...' in rv.headers['Set-Cookie']

    rv = client.get('/cookies', headers={'Cookie': 'fio=...'})
    assert 'Set-Cookie' in rv.headers
    assert 'Expires=Thu, 01 Jan 1970' in rv.headers['Set-Cookie']  # Учитываем правильный формат даты

# ------------------- Параметры URL ----------------------

def test_url_parameters_displayed(client):
    params = {'param1': 'value1', 'param2': 'value2', 'param3': 'value3'}
    rv = client.get('/args', query_string=params)
    content = rv.data.decode('utf-8')

    for key, value in params.items():
        assert f'<td> {key} </td>' in content
        assert f'<td> {value} </td>' in content

# -------------------- Заголовки запроса ----------------

def test_request_headers_displayed(client):
    headers = {
        'Custom-Header-1': 'Value1',
        'Custom-Header-2': 'Value2',
        'Custom-Header-3': 'Value3'
    }
    rv = client.get('/headers', headers=headers)
    content = rv.data.decode('utf-8')

    for key, value in headers.items():
        assert f'<td> {key} </td>' in content
        assert f'<td> {value} </td>' in content

# ---------------------- Параметры формы -----------------

def test_form_parameters_displayed(client):
    data = {'fio': 'Иван Иванов'}
    rv = client.post('/form', data=data)
    content = rv.data.decode('utf-8')

    assert '<td> fio: </td>' in content
    assert '<td> Иван Иванов </td>' in content