from functools import reduce
from collections import namedtuple
import logging
import pytest
import mysql.connector
from app import create_app
from app.db import DBConnector
from app.repositories.role_repository import RoleRepository
from collections import namedtuple

TEST_DB_CONFIG = {
    'MYSQL_USER': 'admin',
    'MYSQL_PASSWORD': 'admin142&hs',
    'MYSQL_HOST': '91.132.58.61',
    'MYSQL_PORT': 3306,
    'MYSQL_DATABASE': 'super_database',
}



def get_connection(app):
    return mysql.connector.connect(
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        host=app.config['MYSQL_HOST']
    )

def setup_db(app):
    logging.getLogger().info("Create db...")
    test_db_name = app.config['MYSQL_DATABASE']
    create_db_query = (f'DROP DATABASE IF EXISTS {test_db_name}; '
                       f'CREATE DATABASE {test_db_name}; '
                       f'USE {test_db_name};')

    with app.open_resource('schema.sql') as f:
        schema_query = f.read().decode('utf8')

    connection = get_connection(app)
    query = '\n'.join([create_db_query, schema_query])
    with connection.cursor(named_tuple=True) as cursor:
        for _ in cursor.execute(query, multi=True):
                pass
    connection.commit()
    connection.close()


def teardown_db(app):
    logging.getLogger().info("Drop db...")
    test_db_name = app.config['MYSQL_DATABASE']
    connection = get_connection(app)
    with connection.cursor() as cursor:
        cursor.execute(f'DROP DATABASE IF EXISTS {test_db_name};')
    connection.close()

#--------------------------------------------------
def init_test_db(connector):
    """Инициализация тестовых таблиц"""
    with connector.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL
                )
            """)
            conn.commit()

def clear_test_db(connector):
    """Очистка тестовых данных"""
    with connector.connect() as conn:
        with conn.cursor() as cursor:
            # Отключаем проверки внешних ключей
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("DELETE FROM roles;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()
#-------------------------------------------------    
@pytest.fixture(scope='session')
def app():
    # Создаём приложение с тестовой конфигурацией
    app = create_app({
        'TESTING': True,
        **TEST_DB_CONFIG
    })
    yield app

@pytest.fixture(scope='session')
def db_connector(app):
    # Создаём временные таблицы вместо пересоздания всей БД
    with app.app_context():
        connector = DBConnector(app)
        init_test_db(connector)  # Новая функция для инициализации тестовых таблиц
        yield connector
        # Не удаляем БД полностью - только очищаем таблицы
        clear_test_db(connector)

@pytest.fixture
def role_repository(db_connector):
    return RoleRepository(db_connector)

@pytest.fixture
def existing_role(db_connector):
    with db_connector.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO roles (name) VALUES ('admin')")
            role_id = cursor.lastrowid
            conn.commit()
    
    yield {'id': role_id, 'name': 'admin'}
    
    with db_connector.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
            conn.commit()

@pytest.fixture
def nonexisting_role_id():
    return 1

@pytest.fixture
def example_roles(db_connector):
    names = ['admin', 'test']
    row_class = namedtuple('Row', ['id', 'name'])

    connection = db_connector.connect()
    roles = []

    with connection.cursor() as cursor:
        for name in names:
            cursor.execute("INSERT INTO roles(name) VALUES (%s)", (name,))
            roles.append(row_class(cursor.lastrowid, name))
        connection.commit()

    yield roles

    with connection.cursor() as cursor:
        ids = ', '.join(str(role.id) for role in roles)
        cursor.execute(f"DELETE FROM roles WHERE id IN ({ids})")
        connection.commit()


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(db_connector):
    # Создаём тестовую роль, если её нет
    with db_connector.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO roles (id, name) VALUES (1, 'admin')")
            # Создаём тестового пользователя
            cursor.execute("""
                INSERT INTO users (username, password, first_name, last_name, role_id)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'hashed_password', 'Admin', 'User', 1))
            conn.commit()
    
    yield
    
    # Очистка после теста
    with db_connector.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE username IN ('admin', 'newuser1')")
            conn.commit()