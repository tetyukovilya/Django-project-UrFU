from django.shortcuts import render
from django.views import View
from .parser import main
from .models import *

from django.shortcuts import render
from django.db.models import Avg, F, Q
from django.db.models.functions import ExtractYear
from .request_bd import *

import requests

from django.db.models import Count
from django.db.models.functions import ExtractYear


# Create your views here.
class StatsPage(View):
    def get(self, request):
        vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
            count=Count('id')).order_by('year')

        vacancies_data = list(vacancies_per_year)
        return render(request, 'Statistics.html',
                      context={"vacancies_per_year": vacancies_data})
        #main()

class SymbolsPage(View):
    def get(self, request):
        vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
            count=Count('id')).order_by('year')

        vacancies_data = list(vacancies_per_year)
        return render(request, '2000Symbols.html',
                      context={"vacancies_per_year": vacancies_data})
        #main()