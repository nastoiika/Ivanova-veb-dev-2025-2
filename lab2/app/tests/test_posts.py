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

def test_posts_template_used(client):
    with captured_templates(app) as templates:
        client.get('/posts')
        assert templates
        template, _ = templates[0]
        assert template.name == "posts.html"

def test_post_template_used(client):
    with captured_templates(app) as templates:
        client.get('/posts/0')
        assert templates
        template, _ = templates[0]
        assert template.name == "post.html"

def test_posts_template_context(client):
    with captured_templates(app) as templates:
        client.get('/posts')
        assert templates
        _, context = templates[0]
        assert "posts" in context
        assert context["posts"] == posts_list

def test_post_template_context(client):
    with captured_templates(app) as templates:
        client.get('/posts/0')
        assert templates
        _, context = templates[0]
        assert "post" in context
        assert context["post"] == posts_list[0]
