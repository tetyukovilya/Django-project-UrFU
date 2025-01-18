from django.db import models


class Profession(models.Model):
    name = models.CharField(max_length=200)
    key_skills = models.TextField()
    salary_from = models.DecimalField(max_digits=10, decimal_places=2)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2)
    salary_currency = models.CharField(max_length=10)
    area_name = models.CharField(max_length=100)
    published_at = models.DateTimeField()

    def __str__(self):
        return self.name
