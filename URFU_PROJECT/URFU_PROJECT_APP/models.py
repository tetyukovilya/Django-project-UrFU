from django.db import models


class Profession(models.Model):
    name = models.CharField(max_length=200)
    key_skills = models.TextField()  # Ключевые навыки
    salary_from = models.DecimalField(max_digits=10, decimal_places=2)  # Зарплата От
    salary_to = models.DecimalField(max_digits=10, decimal_places=2)  # Зарплата До
    salary_currency = models.CharField(max_length=10)  # Валюта зарплаты
    area_name = models.CharField(max_length=100)  # Регион
    published_at = models.DateTimeField()  # Дата публикации

    def __str__(self):
        return self.name
