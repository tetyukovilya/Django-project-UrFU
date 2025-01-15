import requests

def hh_api():
    req = requests.get('https://api.hh.ru/vacancies?per_page=10&professional_role=116')
    data = req.json()
    items = data['items']

    result = []
    for item in items:
        salaries = item.get('salary')

        if salaries is None:
            salaries = {'from': 'Отсутствует', 'to': 'Отсутствует'}
        else:
            # Check for 'from' and 'to' values and set appropriate messages
            from_salary = salaries.get('from')
            to_salary = salaries.get('to')

            if from_salary is None:
                from_salary = 'Отсутствует'
            if to_salary is None:
                to_salary = 'Отсутствует'

            salaries = {
                'from': from_salary,
                'to': to_salary,
                'currency': salaries.get('currency', 'Не указано')
            }

        dict_vacancy = {
            'title': item['name'],
            'company': item['employer']['name'],
            'salary': salaries,
            'link': item['alternate_url'],
        }

        result.append(dict_vacancy)

    return result
