import json
from collections import Counter

from django.shortcuts import render
from django.views import View
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_hh_ru import hh_api
from .parser import main
from .models import *

from django.shortcuts import render
from django.db.models import Avg, F, Q
from django.db.models.functions import ExtractYear
from .request_bd import *
from .models import CurrencyRate
import requests

from django.db.models import Count
from django.db.models.functions import Lower
from django.db.models.functions import ExtractYear
from .parser import fill_currency_table

from URFU_PROJECT_APP.serializers_api import ProfessionSerializer

def get_top_skills():
    top_skills = (Profession.objects.values('name').annotate(skill_count=Count('key_skills')).order_by('-skill_count')[:20])  # Берём только топ-20
    return list(top_skills)

def get_top_skills():
    professions = Profession.objects.all()

    all_skills = []
    for profession in professions:
        skills = profession.key_skills.split('\n')
        all_skills.extend(skill.strip() for skill in skills)

    skill_counts = Counter(all_skills)

    top_skills = skill_counts.most_common(20)
    top_skills_json = json.dumps(top_skills)
    return top_skills_json

# Create your views here.
class StatsPage(View):
    def get(self, request):
        vacancies_by_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(count=Count('id')).order_by('year')
        vacancies_data = list(vacancies_by_year)
        year_sal_data = get_average_salaries_by_year()
        city_sal_data = get_average_salary_by_city()
        top_skills = get_top_skills()
        vacancies_by_city = Profession.objects.values('area_name').annotate(count=Count('id')).order_by('-count')
        vacancies_data_json = json.dumps(list(vacancies_by_city))
        return render(request, 'Statistics.html',
                      context={"vacancies_by_year": vacancies_data, "year_sal_data": year_sal_data, "city_sal_data": city_sal_data, "top_skills": top_skills,
                               'vacancies_data_json': vacancies_data_json})


class SymbolsPage(View):
    def get(self, request):
        #fill_currency_table()
        vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
            count=Count('id')).order_by('year')

        vacancies_data = list(vacancies_per_year)
        return render(request, '2000Symbols.html',
                      context={"vacancies_per_year": vacancies_data})


class JobsPage(View):
    def get(self, request):
        year_sal_data = get_average_salaries_by_year()
        vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
            count=Count('id')).order_by('year')
        vacancies_data = list(vacancies_per_year)
        return render(request, 'Vostrebovannost.html',context={"vacancies_data": vacancies_data, "year_sal_data": year_sal_data})


class LastestVacanciesHH(View):
    def get(self, request):
        items = hh_api()

        context = {
            'items': items,
        }
        return render(request, 'RealTimeVac.html', context)

class GeoPage(View):
    def get(self, request):
        city_sal_data = get_average_salary_by_city()
        vacancies_by_city = Profession.objects.values('area_name').annotate(count=Count('id')).order_by('-count')
        vacancies_data_json = json.dumps(list(vacancies_by_city))
        return render(request, 'Geo.html',context={"city_sal_data": city_sal_data, "vacancies_data_json": vacancies_data_json})

class SkillsPage(View):
    def get(self, request):
        top_skills = get_top_skills()
        return render(request, 'Skills.html',context={"top_skills": top_skills})

class RealTimeVacancies(View):
    def get(self, request):
        return 0#render(request, 'RealTimeVac', context)


class ProfessionAPIView(APIView):

    def get(self, request, pk=None):
        if pk is not None:
            try:
                professions = Profession.objects.get(pk=pk)
                serializer = ProfessionSerializer(professions)
                return Response({'professions': serializer.data}, status=200)
            except Profession.DoesNotExist:
                return Response({'error': 'not found'}, status=404)
            except ValidationError as e:
                return Response({str(e)}, status=400)

        try:
            professions = Profession.objects.all()
            serializer = ProfessionSerializer(professions, many=True)
            return Response({'professions': serializer.data}, status=200)
        except ValidationError as e:
            return Response({str(e)}, status=400)

    def post(self, request):
        try:
            serializer = ProfessionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'post': serializer.data}, status=201)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'PK not found'}, status=400)

        try:
            instance = Profession.objects.get(pk=pk)
        except Profession.DoesNotExist:
            return Response({'error': 'Profession not found'}, status=404)

        serializer = ProfessionSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'profession': serializer.data})

    def delete(self, request, pk=None):
        if pk is not None:
            try:
                profession = Profession.objects.get(pk=pk)
                profession.delete()
                return Response({'message': 'profession deleted'}, status=204)
            except Profession.DoesNotExist:
                return Response({'error': 'not found'}, status=404)
            except ValidationError as e:
                return Response({'error': str(e)}, status=400)


def get_average_salary_by_city():
    # Получаем все вакансии, фильтруя по зарплате
    vacancies = Profession.objects.filter(salary_from__lte=10000000, salary_to__lte=10000000)

    # Создаем словарь для хранения средних зарплат по городам
    average_salaries = {}

    for vacancy in vacancies:
        # Получаем курс валют на первое число месяца вакансии
        first_day_of_month = vacancy.published_at.replace(day=1)
        currency_rate = CurrencyRate.objects.filter(date__lte=first_day_of_month).order_by('-date').first()

        if currency_rate:
            # Конвертируем зарплату в рубли
            salary_in_rub = 0
            if vacancy.salary_currency == 'USD':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.usd
            elif vacancy.salary_currency == 'EUR':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.eur
            elif vacancy.salary_currency == 'KZT':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kzt
            elif vacancy.salary_currency == 'UAH':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uah
            elif vacancy.salary_currency == 'BYR':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.byr
            elif vacancy.salary_currency == 'AZN':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.azn
            elif vacancy.salary_currency == 'UZS':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uzs
            elif vacancy.salary_currency == 'KGS':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kgs
            elif vacancy.salary_currency == 'GEL':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.gel
            else:
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2  # Если валюта рубли

            city = vacancy.area_name  # Получаем город
            if city not in average_salaries:
                average_salaries[city] = {'total_salary': 0, 'count': 0}

            average_salaries[city]['total_salary'] += float(salary_in_rub)
            average_salaries[city]['count'] += 1

    # Рассчитываем средние значения
    for city, data in average_salaries.items():
        average_salaries[city] = data['total_salary'] / data['count']

    # Сортируем по убыванию
    sorted_average_salaries = dict(sorted(average_salaries.items(), key=lambda item: item[1], reverse=True))

    return sorted_average_salaries

def get_average_salaries_by_year():
    # Получаем все вакансии, фильтруя по зарплате
    vacancies = Profession.objects.filter(salary_from__lte=10000000, salary_to__lte=10000000)

    # Создаем словарь для хранения средних зарплат по годам
    average_salaries = {}

    for vacancy in vacancies:
        # Получаем курс валют на первое число месяца вакансии
        first_day_of_month = vacancy.published_at.replace(day=1)
        currency_rate = CurrencyRate.objects.filter(date__lte=first_day_of_month).order_by('-date').first()
        # Конвертируем зарплату в рубли
        salary_in_rub = 0
        if vacancy.salary_currency == 'USD':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.usd
        elif vacancy.salary_currency == 'EUR':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.eur
        elif vacancy.salary_currency == 'KZT':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kzt
        elif vacancy.salary_currency == 'UAH':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uah
        elif vacancy.salary_currency == 'BYR':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.byr
        elif vacancy.salary_currency == 'AZN':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.azn
        elif vacancy.salary_currency == 'UZS':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uzs
        elif vacancy.salary_currency == 'KGS':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kgs
        elif vacancy.salary_currency == 'GEL':
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.gel
        else:
            salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2  # Если валюта рубли

        year = vacancy.published_at.year
        if year not in average_salaries:
            average_salaries[year] = {'total_salary': 0, 'count': 0}

        average_salaries[year]['total_salary'] += float(salary_in_rub)  # Преобразуем в float чтобы js скушал
        average_salaries[year]['count'] += 1

    # Рассчитываем средние значения
    for year, data in average_salaries.items():
        average_salaries[year] = data['total_salary'] / data['count']

    return average_salaries