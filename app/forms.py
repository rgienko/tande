from django import forms

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


class EditEngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement

        fields = ['provider', 'parent', 'start_date',
                  'time_code', 'budget_hours', 'fye', 'type', 'srg_id']

        widgets = {
            'fye': DatePickerInput,
            'start_date': DatePickerInput
        }


class CompleteEngagementForm(forms.ModelForm):
    class Meta:
        model = Engagement

        fields = ['is_complete']

        labels = {
            'is_complete': _('Is Complete')
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignments

        fields = ['engagement', 'assignee']


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time

        fields = ['date', 'hours', 'time_type_id', 'note']

        labels = {
            'date': _('Date'),
            'hours': _('Hours'),
            'time_type_id': _('Type'),
            'note': _('Note')
        }

        widgets = {
            'note': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'date': DatePickerInput()
        }


class EditTimeForm(forms.ModelForm):
    class Meta:
        model = Time

        fields = ['engagement', 'date', 'hours', 'note']

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


class NewTimeCodeForm(forms.ModelForm):
    class Meta:
        model = Timecode

        fields = ['time_code', 'time_code_desc', 'time_code_hours']

        labels = {
            'time_code': _('Time Code'),
            'time_code_desc': _('Description'),
            'time_code_hours': _('Hours Budget')
        }

        widgets = {
            'time_code': forms.TextInput(attrs={'size': 5}),
            'time_code_desc': forms.TextInput(attrs={'size': 75}),
            'time_code_hours': forms.TextInput(attrs={'size': 5})
        }


class EditTimeCodeForm(forms.ModelForm):
    class Meta:
        model = Timecode

        fields = ['time_code_desc', 'time_code_hours']

        labels = {
            'time_code_desc': _('Description'),
            'time_code_hours': _('Hours Budget')
        }

        widgets = {
            'time_code_desc': forms.TextInput(attrs={'size': 75}),
            'time_code_hours': forms.TextInput(attrs={'size': 5})
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
            'todo_date': DatePickerInput()
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense

        fields = ['expense_category', 'expense_amount']

        labels = {
            'engagement': _('Engagement'),
            'expense_category': _('Category'),
            'expense_amount': _('Amount')
        }
