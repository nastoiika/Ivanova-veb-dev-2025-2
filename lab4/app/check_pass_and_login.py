import re

def check_password(password):
    if not(password):
        return False
    
    if not 8 <= len(password) <= 128:
        return False

    if ' ' in password:
        return False

    if not re.search(r'[A-ZА-Я]', password):
        return False

    if not re.search(r'[a-zа-я]', password):
        return False

    if not re.search(r'\d', password):
        return False

    if re.search(r'[^\wА-Яа-яЁё~!?@#$%^&*_\-+\[\]{}()<>\.,:;\\/|"\']', password):
        return False

    return True

def check_login(username):
    if not(username):
        return False
    
    if ' ' in username:
        return False
    
    if not re.fullmatch(r'[A-Za-z0-9]{5,}', username):
        return False
    return True