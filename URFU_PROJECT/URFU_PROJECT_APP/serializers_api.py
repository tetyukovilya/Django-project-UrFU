from rest_framework import serializers

from .models import Profession


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
        read_only_fields = ['published_at']
