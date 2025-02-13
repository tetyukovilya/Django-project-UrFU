"""
URL configuration for URFU_PROJECT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from URFU_PROJECT_APP.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stats', StatsPage.as_view()),
    path('symbols', SymbolsPage.as_view()),
    path('jobs', JobsPage.as_view()),
    path('geo', GeoPage.as_view()),
    path('skills', SkillsPage.as_view()),
    path('rtvacancies', LastestVacanciesHH.as_view()),
    path('api/professions/', ProfessionAPIView.as_view(), name='profession-list'),
    path('api/professions/<int:pk>/', ProfessionAPIView.as_view(), name='profession-detail')
]
