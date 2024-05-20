import csv


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
    flag = 0
    with open('countries_data.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = ''.join(i for i in row)
            name = name.replace('\ufeff', '')
            if country == name:
                flag = 1
                break
    if flag == 1:
        return True
    return False


def city_check(city):
    if not isinstance(city, str):
        return False
    flag = 0
    with open('cities.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = ''.join(i for i in row)
            name = name.replace('\ufeff', '')
            if city == name:
                flag = 1
                break
    if flag == 1:
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


def city_point_check(city):
    if not isinstance(city, str):
        return False
    with open('cities.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = ''.join(i for i in row)
            name = name.replace('\ufeff', '')
            if city == name:
                return True
    return False

def country_point_check(country):
    if not isinstance(country, str):
        return False
    with open('countries_data.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name = ''.join(i for i in row)
            name = name.replace('\ufeff', '')
            if country == name:
                return True
    return False