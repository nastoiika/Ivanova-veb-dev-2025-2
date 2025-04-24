import pytest
from app import create_app
from flask import url_for


@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        with app.app_context():
            yield client



def test_show_user(client):
    # Заходим на страницу списка пользователей без авторизации
    response = client.get('/users', follow_redirects=True)
    assert response.status_code == 200
    page = response.data.decode('utf-8')

    # Проверяем наличие кнопки "View"
    assert 'View' in page

    # Переходим на страницу просмотра пользователя с id=1
    response = client.get('/users/10', follow_redirects=True)
    assert response.status_code == 200
    user_page = response.data.decode('utf-8')

    assert 'Логин' in user_page
    assert 'Имя' in user_page
    assert 'Отчество' in user_page
    assert 'Фамилия' in user_page
    assert 'Роль' in user_page
    assert 'Дата регистрации' in user_page


def test_create_user(client):
    response = client.get('/users', follow_redirects=True)
    user_page = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Добавить пользователя' not in user_page

    # Авторизация пользователя для теста
    client.post('/auth/login', data={
        'username': 'admin', 
        'password': 'Qwerty123'
    }, follow_redirects=True)

    # Проверка, что страница создания пользователя доступна после входа
    response = client.get('/users', follow_redirects=True)
    user_page = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Добавить пользователя' in user_page

    # Заполнение формы с правильными данными
    response = client.post('/users/new', data={
        'username': 'newuser',
        'password': 'Pass12345!',
        'first_name': 'Иван',
        'middle_name': 'Иванович',
        'last_name': 'Иванов',
        'role_id': '1'
    }, follow_redirects=True)
    
    # Проверка успешного редиректа на страницу со списком пользователей и появления нового пользователя
    assert response.status_code == 200
    assert 'newuser' in response.data.decode('utf-8')

    # Тест с ошибкой - неправильный логин
    response = client.post('/users/new', data={
        'username': '',
        'password': ' ',
        'first_name': 'Иван',
        'middle_name': 'Иванович',
        'last_name': 'Иванов',
        'role_id': '1'
    }, follow_redirects=True)

    # Проверка, что форма не отправлена, и ошибка отображена
    assert 'Введен недопустимый логин или пароль' in response.data.decode('utf-8')


def test_edit_user(client):
    client.post('/auth/login', data={
        'username': 'newuser', 
        'password': 'Pass12345!'
    }, follow_redirects=True)


    # Открываем страницу редактирования
    response = client.get(f"/users/10/edit")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    
    # Проверяем, что в форме есть нужные поля и заполнены текущими значениями
    assert 'name="first_name"' in html and 'value="Петр"' in html
    assert 'name="middle_name"' in html and 'value="Петрович"' in html
    assert 'name="last_name"' in html and 'value="Сидоров"' in html

    # Проверяем, что полей логина и пароля нет
    assert 'name="username"' not in html
    assert 'name="password"' not in html

    # Отправляем измененные данные
    response = client.post(f"/users/10/edit", data={
        "first_name": "Петр",
        "middle_name": "Петрович",
        "last_name": "Сидоров",
        "role_id": "1"
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Убедимся, что был показан flash с успехом
    assert 'Учетная запись изменена' in response.data.decode('utf-8')

    # Убедимся, что на странице списка обновленные данные есть
    response = client.get('/users', follow_redirects=True)
    user_page = response.data.decode('utf-8')
    assert "Петр" in user_page

def test_edit_user_unauthenticated(client):
    # Неавторизованный доступ
    response = client.get("/users/1/edit", follow_redirects=True)
    assert response.status_code == 200
    assert "Необходимо авторизоваться" in response.data.decode("utf-8")

def test_delete_user(client, app, db_connector):
    # 1. Подготовка тестовых данных (создаём роль, если её нет)
    with db_connector.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO roles (id, name) VALUES (1, 'admin')")
            conn.commit()

    # 2. Авторизация пользователя для теста
    client.post('/auth/login', data={
        'username': 'admin', 
        'password': 'Qwerty123'
    }, follow_redirects=True)

    # 3. Создаем нового пользователя для удаления
    response = client.post('/users/new', data={
        'username': 'newuser1',
        'password': 'Pass12345!',
        'first_name': 'Иван',
        'middle_name': 'Иванович',
        'last_name': 'Иванов',
        'role_id': '1'  # Убедитесь, что роль с ID=1 существует
    }, follow_redirects=True)
    
    # Проверяем, что пользователь создан (HTTP-код и отображение в интерфейсе)
    assert response.status_code == 200
    assert 'newuser1' in response.data.decode('utf-8')
    
    # 4. Проверяем, что пользователь действительно есть в БД
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db_connector)
    all_users = user_repo.all()
    
    print("Все пользователи в БД:", all_users)  # Отладочный вывод
    
    user_to_delete = next((u for u in all_users if u['username'] == 'newuser1'), None)
    assert user_to_delete is not None, f"Пользователь не найден в БД. Все пользователи: {all_users}"
    
    # 5. Удаляем пользователя
    user_id = user_to_delete['id']
    response = client.post(f"/users/{user_id}/delete", follow_redirects=True)
    
    # Проверяем результат удаления
    assert response.status_code == 200
    assert "Учетная запись удалена" in response.data.decode("utf-8")
    assert 'newuser1' not in response.data.decode('utf-8')

def test_change_password(client, app, db_connector):

    client.post('/auth/login', data={
        'username': 'admin', 
        'password': 'Qwerty123'
    }, follow_redirects=True)
    
    response = client.get(f'/users/2/change')
    assert response.status_code == 200
    assert 'Введите старый пароль' in response.data.decode('utf-8')

    response = client.post(f'/users/2/change', data={
        'old_password': 'Qwerty123',
        'new_password': 'Qwerty123!',
        'copy_password': 'Qwerty123!'
    }, follow_redirects=True)

    assert response.status_code == 200

    client.get('/auth/logout', follow_redirects=True)
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'Qwerty123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    