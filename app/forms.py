from django import forms

from . import widget
from .models import *
from .widget import *
from django.utils.translation import gettext_lazy as _


class EngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement

        fields = ['provider', 'parent', 'start_date',
                  'time_code', 'fye', 'type']

        widgets = {
            'fye': DatePickerInput,
            'start_date': DatePickerInput
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignments

        fields = ['engagement', 'assignee']
