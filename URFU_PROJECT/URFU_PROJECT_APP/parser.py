import pandas as pd

from .models import Profession


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