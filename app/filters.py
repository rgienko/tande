import django_filters
from django_filters.widgets import RangeWidget

from app.models import Time


class TimesheetFilter(django_filters.FilterSet):
    # employee = django_filters.CharFilter(field_name='employee')
    # engagement__provider = django_filters.CharFilter(field_name='engagement', lookup_expr='icontains')
    period = django_filters.DateFromToRangeFilter(field_name='date', widget=RangeWidget(attrs={'placeholder': 'DD/MM/YYY'}))

    class Meta:
        model = Time
        fields = ['employee']


