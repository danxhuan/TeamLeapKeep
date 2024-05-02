def username_check(name):
    if not isinstance(name, str):
        return False
    letters = [i for i in name if not (i.isdigit()) and not (i.isalpha())]
    if len(letters) != 0:
        return False
    return True


def email_check(email):
    if not isinstance(email, str):
        return False
    letters = [i for i in email if not (
        i.isdigit()) and not (i.isalpha()) and i not in '._-@']
    if len(letters) != 0:
        return False
    return True


def country_check(country):
    if not isinstance(country, str):
        return False
    if all(i.isalpha() for i in country.replace(' ', '')):
        return True
    return False


def password_check(password):
    if len(password) < 6 or len(password) > 30:
        return False
    if len([i for i in password if i.isdigit()]) == 0:
        return False
    if password.count(' ') != 0:
        return False
    return True
