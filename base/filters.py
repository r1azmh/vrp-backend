import django_filters
from . import models


class WorkFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Work
        fields = ['name']
