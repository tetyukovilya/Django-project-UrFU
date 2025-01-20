from django.db import models


class Profession(models.Model):
    name = models.CharField(max_length=200)
    key_skills = models.TextField()
    salary_from = models.DecimalField(max_digits=10, decimal_places=2)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2)
    salary_currency = models.CharField(max_length=10)
    area_name = models.CharField(max_length=100)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CurrencyRate(models.Model):
    date = models.DateField(unique=True)  # Поле для хранения даты
    usd = models.DecimalField(max_digits=10, decimal_places=4)
    eur = models.DecimalField(max_digits=10, decimal_places=4)
    kzt = models.DecimalField(max_digits=10, decimal_places=4)
    uah = models.DecimalField(max_digits=10, decimal_places=4)
    byr = models.DecimalField(max_digits=10, decimal_places=4)
    azn = models.DecimalField(max_digits=10, decimal_places=4)
    uzs = models.DecimalField(max_digits=10, decimal_places=4)
    kgs = models.DecimalField(max_digits=10, decimal_places=4)
    gel = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"Курсы валют на {self.date}"
