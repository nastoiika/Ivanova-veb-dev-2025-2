import random
from ssl import SSLSession
from flask import Flask, render_template, abort, request, make_response
from faker import Faker
import re

fake = Faker()

app = Flask(__name__)
application = app

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

@app.route('/headers')
def headers():
    return render_template('headers.html', title='Заголовки запроса')

@app.route('/args')
def args():
    return render_template('args.html', title='Параметры URL')

@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html', title='Cookies'))
    if 'fio' not in request.cookies:
        resp.set_cookie('fio', '...')
    else:
        resp.set_cookie('fio', expires=0)
    return resp

@app.route('/form', methods=["GET","POST"])
def form():
    return render_template('form.html', title='Параметры формы')

@app.route('/counter')
def counter():
    if session.get("counter"):
        session['counter'] += 1
    else:
        session['counter'] = 1
    return render_template('counter.html')

@app.route('/number', methods=["GET", "POST"])
def number():
    error = None 
    allowed_chars = r'^[\d\s\(\)\-\.\+]+$'
    cleaned_number = ""

    if request.method == 'POST':
        number = request.form.get("number")
        cleaned_number = re.sub(r'[\s\(\)\-\.+]', '', number)

        if re.search(r'[^\d\s\(\)\-\.\+]', number):
            error = "Недопустимые символы"
        elif cleaned_number.startswith(('8', '7')) and len(cleaned_number) != 11:
            error = "Неверное количество цифр"
        elif not cleaned_number.startswith(('8', '7')) and len(cleaned_number) != 10:
            error = "Неверное количество цифр"
        else:
            cleaned_number = '8' + cleaned_number[-10:]
    
    return render_template('number.html', title='Проверка номера телефона', error=error, cleaned_number=cleaned_number)

if __name__ == '__main__':
    app.run(debug=True)