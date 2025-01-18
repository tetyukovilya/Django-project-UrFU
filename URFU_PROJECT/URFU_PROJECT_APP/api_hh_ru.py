import requests
import re
from datetime import datetime


def fetch_vacancies():
    url = 'https://api.hh.ru/vacancies?per_page=10&professional_role=116&order_by=publication_time&text=безопасность, защита, information security, cyber security'
    response = requests.get(url)
    return response.json()['items']


def vacancy_details(vacancy_id):
    url = f'https://api.hh.ru/vacancies/{vacancy_id}'
    return requests.get(url).json()


def extract_salary(salary):
    if salary is None:
        return {'from': 'Отсутствует', 'to': 'Отсутствует', 'currency': 'Не указано'}

    from_sal = salary.get('from', 'Отсутствует')
    to_sal = salary.get('to', 'Отсутствует')

    return {
        'from': from_sal,
        'to': to_sal,
        'currency': salary.get('currency', 'Не указано'),
    }


def clean_description(html_text):
    return re.sub(r'<.*?>', '', html_text)


def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
    return date_obj.strftime("%d.%m.%Y, %H:%M")


def get_logo(logos):
    return logos['240'] if logos else 'static/img/empty_company.png'

def get_city(city_info):
    return city_info['city'] if city_info else 'Пусто'

def hh_api():
    vacancies = fetch_vacancies()
    result = []

    for item in vacancies:
        vacancy_id = item.get('id')
        more_data = vacancy_details(vacancy_id)

        dict_vacancy = {
            'title': item['name'],
            'company': item['employer']['name'],
            'salary': extract_salary(item.get('salary')),
            'link': item['alternate_url'],
            'logo': get_logo(item['employer']['logo_urls']),
            'desc': clean_description(more_data['description']),
            'city': get_city(item.get('address')),
            'experience': item.get('experience', {}).get('name', 'Не указано'),
            'skills': [skill['name'] for skill in more_data['key_skills']],
            'date': format_date(item['published_at']),
        }

        result.append(dict_vacancy)

    return result
