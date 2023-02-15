from django import forms

from .models import *
from .widget import *
from django.utils.translation import gettext_lazy as _
from bootstrap_datepicker_plus.widgets import DateTimePickerInput


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


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time

        fields = ['date', 'hours', 'note']

        labels = {
            'date': _('Date'),
            'hours': _('Hours'),
            'note': _('Note')
        }

        widgets = {
            'note': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'date': DatePickerInput()
        }


class EditTimeForm(forms.ModelForm):
    class Meta:
        model = Time

        fields = ['engagement','date', 'hours', 'note']

        labels = {
            'engagement': _('Engagement'),
            'date': _('Date'),
            'hours': _('Hours'),
            'note': _('Note')
        }

        widgets = {
            'note': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'date': DatePickerInput()
        }


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todolist

        fields = ['todo_date', 'anticipated_hours', 'note']

        labels = {
            'todo_date': _('Start Date'),
            'anticipated_hours': _('Expected Hours'),
            'note': _('Note')
        }

        widgets = {
            'note': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'start_date': DatePickerInput()
        }
