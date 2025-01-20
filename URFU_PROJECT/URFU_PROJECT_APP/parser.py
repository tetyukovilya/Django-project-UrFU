from django.contrib.sites import requests
from .models import Profession, CurrencyRate
import pandas as pd
from collections import Counter
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


def main():
    df = pd.read_csv('vacancies_2024.csv', low_memory=False)
    keywords = [
        'безопасность', 'защита', 'information security specialist', 'information security', 'фахівець служби безпеки',
         'cyber security'
    ]
    pattern = '|'.join(keywords)

    # Фильтруем DataFrame

    filtered_df = df[df['name'].str.contains(pattern, case=False, na=False)]
    filtered_df = filtered_df.dropna()
    objects = [Profession(**row) for index, row in filtered_df.iterrows()]

    # Сохранение объектов в базе данных
    Profession.objects.bulk_create(objects)


# функция для заполнения таблицы CurrencyRate (где хранятся курсы валют)
def fill_currency_table():
    """Заполняет таблицу данными из таблицы Profession."""
    # Получаем уникальные даты
    professions = Profession.objects.values_list('published_at', flat=True).distinct()

    # Уникальные даты с первым числом месяца
    unique_dates = set()
    for published_at in professions:
        first_day_of_month = published_at.replace(day=1)  # Устанавливаем день на 1
        unique_dates.add(first_day_of_month.date())  # Приводим к дате и добавляем в множество

    # Словарь для хранения курсов валют по датам
    currency_rates = {}

    # Получаем курсы валют для каждой уникальной даты
    for date in unique_dates:
        currencies = ['USD', 'EUR', 'KZT', 'UAH', 'BYR', 'AZN', 'UZS', 'KGS', 'GEL']  # Список валют
        rates = get_exchange_rates(currencies, date)

        # Сохраняем курсы валют в словаре
        currency_rates[date] = {
            'usd': rates.get('USD', 0),
            'eur': rates.get('EUR', 0),
            'kzt': rates.get('KZT', 0),
            'uah': rates.get('UAH', 0),
            'byr': rates.get('BYR', 0),
            'azn': rates.get('AZN', 0),
            'uzs': rates.get('UZS', 0),
            'kgs': rates.get('KGS', 0),
            'gel': rates.get('GEL', 0),
        }

    # Создаем записи в таблице CurrencyRate
    currency_rate_objects = []
    for date, rates in currency_rates.items():
        currency_rate_objects.append(CurrencyRate(
            date=date,
            usd=rates['usd'],
            eur=rates['eur'],
            kzt=rates['kzt'],
            uah=rates['uah'],
            byr=rates['byr'],
            azn=rates['azn'],
            uzs=rates['uzs'],
            kgs=rates['kgs'],
            gel=rates['gel'],
        ))

    # Используем bulk_create для массового добавления записей
    CurrencyRate.objects.bulk_create(currency_rate_objects)



def get_exchange_rates(currencies, date):
    """Получает курсы валют для заданных валют и даты."""
    date_str = date.strftime('%d/%m/%Y')
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"

    print(f"Запрос к API для даты: {date_str}, валюты: {currencies}")

    try:
        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        rates = {}
        for valute in root.findall('Valute'):
            code = valute.find('CharCode').text
            if code in currencies:
                value = float(valute.find('Value').text.replace(',', '.'))
                nominal = int(valute.find('Nominal').text)
                rates[code] = value / nominal

        return rates

    except ET.ParseError:
        print("Ошибка при парсинге XML-ответа")

    return {}
