from .models import Profession
from django.db.models import Count


def get_cities_data():

    total_vacancies = Profession.objects.count()

    cities_data = (
        Profession.objects
        .values('area_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    for city in cities_data:
        city['percentage'] = (city['count'] / total_vacancies) * 100

    return list(cities_data)
