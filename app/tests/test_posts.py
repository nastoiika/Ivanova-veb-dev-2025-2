import pytest
from app import app, posts_list


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    rv = client.get('/')
    assert 'Лабораторная работа № 1'.encode('utf-8') in rv.data

def test_posts_page(client):
    rv = client.get('/posts')
    assert 'Посты'.encode('utf-8') in rv.data
    for post in posts_list:
        assert post['title'].encode('utf-8') in rv.data
        assert post['author'].encode('utf-8') in rv.data
        assert post['date'].strftime('%d.%m.%Y').encode('utf-8') in rv.data
        assert f'images/{post["image_id"]}'.encode('utf-8') in rv.data

def test_post_page(client):
    for index, post in enumerate(posts_list):
        rv = client.get(f'/posts/{index}')
        assert post['title'].encode('utf-8') in rv.data
        assert post['author'].encode('utf-8') in rv.data
        assert post['date'].strftime('%d.%m.%Y').encode('utf-8') in rv.data
        assert post['text'].encode('utf-8') in rv.data

def test_nonexistent_post(client):
    rv = client.get('/posts/1000')
    assert rv.status_code == 404