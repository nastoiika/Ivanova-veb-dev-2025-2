def test_get_by_id_with_existing_role(role_repository, existing_role):
    role = role_repository.get_by_id(existing_role['id'])
    assert role['id'] == existing_role['id']
    assert role['name'] == existing_role['name']

def test_get_by_id_with_nonexisting_role(role_repository):
    role = role_repository.get_by_id(99999)  # Заведомо несуществующий ID
    assert role is None


def test_all_with_nonempty_db(role_repository, existing_role):
    """Тест проверяет, что метод all возвращает полные данные"""
    roles = role_repository.all()
    assert len(roles) > 0
    found_roles = [r for r in roles if r['id'] == existing_role['id']]
    assert len(found_roles) == 1
    assert found_roles[0]['name'] == existing_role['name']