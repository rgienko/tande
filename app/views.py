import datetime
import os
from datetime import timedelta

import pandas
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_pandas.io import read_frame
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
from django.core.cache import cache

import calendar
from calendar import HTMLCalendar


from django.contrib.auth.mixins import LoginRequiredMixin
# from sendgrid import SendGridAPIClient

from .filters import TimesheetFilter
from .forms import *
from .models import *


# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if request.user.is_staff:
                return redirect('admin-dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Error, wrong username or password.')
        return render(request, 'login.html')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        username = first_name + "." + last_name
        email = username + "@srgroupllc.com"
        if password1 == password2:
            new_user = User.objects.create_user(username, email, password1)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()

            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
    else:
        pass

    return render(request, 'register.html')


def resetPassword(request):
    SENDGRID_API_KEY = os.environ["SENDGRID_KEY"]
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=data))
            if associated_user.exists():
                for user in associated_user:
                    msg = EmailMessage(
                        from_email='Randall.Gienko@srgroupllc.com',
                        to=[user.email, ]
                    )

                    protocol = 'http://'
                    domain = '127.0.0.1:8000/accounts/reset/'
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    user = user
                    token = default_token_generator.make_token(user)

                    msg.template_id = "d-31d5b59a90454aaa8cd685b7011ce213"
                    msg.dynamic_template_data = {
                        "title": 'Password Reset',
                        "protocol": protocol,
                        "domain": domain,
                        "uid": uid,
                        "token": token,
                        "reset_url": protocol + domain + uid + "/" + token
                    }
                    msg.send(fail_silently=False)

                    return redirect("/accounts/password_reset/done")
                    # sg = SendGridAPIClient(SENDGRID_API_KEY)
                    # sg.send(msg)

    password_reset_form = PasswordResetForm()
    context = {'password_reset_form': password_reset_form}
    return render(request, 'password_reset.html', context)


class Dashboard(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    redirect_field_name = 'dashboard/'
    template_name = 'dashboard.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):
        add_time_form = TimeForm(self.request.POST)
        add_expense_form = ExpenseForm(self.request.POST)
        complete_engagement_form = CompleteEngagementForm(self.request.POST)

        # cache_key = f'all_engagements_{self.request.user.id}'
        # all_engagements = cache.get(cache_key)
        # if all_engagements is None:

        # if self.request.user.is_staff: all_engagements = Engagement.objects.all() else: all_engagements =
        # Engagement.objects.raw( 'SELECT * FROM app_engagement JOIN app_assignments ON app_assignments.engagement_id
        # = app_engagement.engagement_id WHERE app_assignments.assignee_id = {userid};'.format(
        # userid=self.request.user.id))

        all_engagements = Assignments.objects.select_related('engagement').filter(assignee=self.request.user.id)

        for engagement in all_engagements:
            engagement_time_sheet_entries = Time.objects.filter(engagement=engagement.engagement_id)

            engagement_time_sheet_by_employee = engagement_time_sheet_entries.values('employee__user__username',
                                                                                     'employee__rate').annotate(
                engagement_emp_hours=Sum('hours')).order_by('-engagement_emp_hours')

            engagement.staff = Assignments.objects.filter(engagement=engagement.engagement_id)

            engagement.engagement_time_sheet_entries = engagement_time_sheet_by_employee

            engagement_total_hours = engagement_time_sheet_entries.aggregate(
                project_hours=Sum('hours'))

            engagement.engagement_hours = engagement_total_hours

        # cache.set(cache_key, all_engagements, timeout=30)

        context = {'today': self.today, 'week_beg': self.week_beg, 'week_end': self.week_end,
                   'all_engagements': all_engagements, 'add_time_form': add_time_form,
                   'add_expense_form': add_expense_form, 'complete_engagement_form': complete_engagement_form}

        return self.render_to_response(context)

    # noinspection DuplicatedCode
    def post(self, *args, **kwargs):
        # noinspection DuplicatedCode
        engagement_id = self.request.POST.get('engagement-input')
        engagement_instance = get_object_or_404(Engagement, srg_id=engagement_id)
        employee_instance = get_object_or_404(Employee, user_id=self.request.user.id)

        add_time_form = TimeForm(self.request.POST)
        add_expense_form = ExpenseForm(self.request.POST)
        complete_engagement_form = CompleteEngagementForm(self.request.POST, instance=engagement_instance)

        print(employee_instance)

        if add_time_form.is_valid():
            new_entry = add_time_form.save(commit=False)
            new_entry.employee = employee_instance
            # new_entry.date = self.today
            new_entry.engagement = engagement_instance
            new_entry.save()
            return redirect(reverse_lazy('dashboard'))

        elif add_expense_form.is_valid():
            new_expense = add_expense_form.save(commit=False)
            new_expense.employee = employee_instance
            new_expense.engagement = engagement_instance
            new_expense.save()
            return redirect(reverse_lazy('dashboard'))

        elif complete_engagement_form.is_valid:
            engagement_instance = complete_engagement_form.save(commit=False)
            engagement_instance.save()

            return redirect(reverse_lazy('dashboard'))

        context = {'add_time_form': add_time_form, 'add_expense_form': add_expense_form,
                   'complete_engagement_form': complete_engagement_form}

        return self.render_to_response(context)


class AdminDashboard(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'admin_dashboard.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):

        all_parents = Parent.objects.all()

        for parent in all_parents:
            parent.parent_engagements = Engagement.objects.filter(parent=parent.parent_id)

            for engagement in parent.parent_engagements:
                engagement_time_sheet_entries = Time.objects.filter(engagement=engagement.engagement_id)

                engagement_time_sheet_by_employee = engagement_time_sheet_entries.values('employee__user__username',
                                                                                         'employee__rate').annotate(
                    engagement_emp_hours=Sum('hours')).order_by('-engagement_emp_hours')

                # engagement.staff = Assignments.objects.filter(engagement=engagement.engagement_id)

                engagement.engagement_time_sheet_entries = engagement_time_sheet_by_employee

                engagement_total_hours = engagement_time_sheet_entries.aggregate(
                    project_hours=Sum('hours'))

                engagement.engagement_hours = engagement_total_hours

        context = {'today': self.today, 'week_beg': self.week_beg,
                   'week_end': self.week_end, 'all_parents': all_parents}

        return self.render_to_response(context)


class Timesheet(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    redirect_field_name = 'timesheet/'
    template_name = 'timesheet.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):
        timesheet_entries = Time.objects.filter(employee__user_id=self.request.user.id).filter(
            date__gte=self.week_beg).filter(
            date__lte=self.week_end)

        weekly_total = timesheet_entries.values().aggregate(weekly_hours_total=Sum('hours'))

        add_time_form = TimeForm(self.request.POST)

        context = {'today': self.today, 'week_beg': self.week_beg,
                   'week_end': self.week_end, 'timesheet_entries': timesheet_entries,
                   'add_time_form': add_time_form, 'weekly_total': weekly_total}

        return self.render_to_response(context)

    # noinspection DuplicatedCode
    def post(self, *args, **kwargs):
        # noinspection DuplicatedCode
        add_time_form = TimeForm(self.request.POST)
        engagement_id = self.request.POST.get('engagement-input')

        engagement_instance = get_object_or_404(Engagement, srg_id=engagement_id)
        employee_instance = get_object_or_404(Employee, user_id=self.request.user.id)

        if add_time_form.is_valid():
            new_entry = add_time_form.save(commit=False)
            new_entry.employee = employee_instance
            new_entry.engagement = engagement_instance
            new_entry.save()
            return redirect(reverse_lazy('timesheet'))

        context = {'add_time_form': add_time_form}

        return self.render_to_response(context)


class TodolistView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    # redirect_field_name = 'dashboard/'
    template_name = 'todolist.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=28)

    def get(self, *args, **kwargs):
        assigned_engagements = Assignments.objects.select_related('engagement').filter(assignee=self.request.user.id)
        current_todolist = Todolist.objects.filter(employee__user_id=self.request.user.id).filter(todo_date__gte=self.week_beg)
        add_todo_form = TodoForm(self.request.POST)

        context = {'today': self.today, 'week_beg': self.week_beg, 'week_end': self.week_end,
                   'assigned_engagements': assigned_engagements, 'add_todo_form': add_todo_form,
                   'current_todo_list': current_todolist}

        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        engagement_id = self.request.POST.get('engagement-input')
        engagement_instance = get_object_or_404(Engagement, srg_id=engagement_id)
        employee_instance = get_object_or_404(Employee, user_id=self.request.user.id)

        add_todo_form = TodoForm(self.request.POST)

        if add_todo_form.is_valid():
            new_entry = add_todo_form.save(commit=False)
            new_entry.employee = employee_instance
            new_entry.engagement = engagement_instance
            new_entry.save()
            return redirect(reverse_lazy('todolist'))

        context = {'add_todo_form': add_todo_form}

        return self.render_to_response(context)


class TodolistViewAdmin(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    # redirect_field_name = 'dashboard/'
    template_name = 'admin_todolist.html'

    today = date.today()
    month_number = today.month
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=28)

    week_period_start = today + timedelta(days=7)
    week_period_end = today + timedelta(days=35)

    next_week_days = []

    employees_todolist = Todolist.objects.values('todo_date', 'employee', 'engagement').filter(
        todo_date__gte=week_period_start)

    for count, i in enumerate(range(0, 5)):
        if count == 0:
            next_week_days.append(week_beg + timedelta(days=7))
        else:
            next_day = week_beg + timedelta(days=count)
            next_week_days.append(next_day + timedelta(days=7))

    def get(self, *args, **kwargs):
        srg_todo_list = Todolist.objects.filter(todo_date__year=2023).order_by('employee__user__username')
        employees = Employee.objects.all().order_by('user__first_name')

        for emp in employees:
            emp.emp_todo_list_day_one = srg_todo_list.filter(employee__user_id=emp.user_id).filter(
                todo_date=self.week_beg + timedelta(days=7))
            emp.emp_todo_list_day_two = srg_todo_list.filter(employee__user_id=emp.user_id).filter(
                todo_date=self.week_beg + timedelta(days=8))
            emp.emp_todo_list_day_three = srg_todo_list.filter(employee__user_id=emp.user_id).filter(
                todo_date=self.week_beg + timedelta(days=9))
            emp.emp_todo_list_day_four = srg_todo_list.filter(employee__user_id=emp.user_id).filter(
                todo_date=self.week_beg + timedelta(days=10))
            emp.emp_todo_list_day_five = srg_todo_list.filter(employee__user_id=emp.user_id).filter(
                todo_date=self.week_beg + timedelta(days=11))

        # srg_todo_list = Todolist.objects.filter(todo_date__year=2023).order_by('employee__user__username')
        # print(srg_todo_list)

        context = {'today': self.today, 'week_beg': self.week_beg, 'week_end': self.week_end,
                   'next_week_days': self.next_week_days, 'employees': employees, 'srg_todo_list': srg_todo_list}

        return self.render_to_response(context)


@login_required(login_url='/login')
def createEngagement(request):
    if request.method == 'POST':

        form = EngagementForm(request.POST)

        who = request.POST.get('provider')
        what = request.POST.get('time_code')
        when = request.POST.get('fye')
        how = request.POST.get('type')
        print(when)

        if when == '':
            srg_id = who + "." + str(what) + "." + how
        else:
            when = when[:4]
            srg_id = who + "." + str(what) + "." + str(
                when) + "." + how

        if form.is_valid():
            new_engagement = form.save(commit=False)
            new_engagement.srg_id = srg_id
            new_engagement.save()

            return redirect('add-assignments', new_engagement.engagement_id)

    else:
        form = EngagementForm()

    context = {'form': form}

    return render(request, 'create_engagement.html', context)


@login_required(login_url='/login')
def createAssignments(request, pk):
    engagement_instance = get_object_or_404(Engagement, pk=pk)
    srgid = engagement_instance.engagement_id
    already_assigned = Assignments.objects.select_related('assignee').filter(engagement=engagement_instance)

    if request.method == 'POST' and 'assign_continue_button' in request.POST:
        form = AssignmentForm(request.POST)
        if form.is_valid():
            new_assignment = form.save(commit=False)
            new_assignment.save()

            return redirect('dashboard')

    elif request.method == 'POST' and 'assign_another_button' in request.POST:
        form = AssignmentForm(request.POST)
        if form.is_valid():
            new_assignment = form.save(commit=False)
            new_assignment.save()

            return redirect('add-assignments', engagement_instance.engagement_id)

    else:

        form = AssignmentForm(initial={'engagement': srgid})

    context = {'engagement_instance': engagement_instance, 'form': form, 'already_assigned': already_assigned}

    return render(request, 'create_assignments.html', context)


@login_required(login_url='/login')
def editTimesheet(request, pk):
    timesheet_instance = get_object_or_404(Time, pk=pk)

    if request.method == 'POST':
        edit_time_form = EditTimeForm(request.POST, instance=timesheet_instance)

        if edit_time_form.is_valid():
            timesheet_instance = edit_time_form.save(commit=False)
            timesheet_instance.save()

            return redirect('timesheet')
    else:
        edit_time_form = EditTimeForm(instance=timesheet_instance)

    context = {'edit_time_form': edit_time_form}

    return render(request, 'edit_timesheet.html', context)


class EngagementDashboard(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    # redirect_field_name = ''
    template_name = 'engagements.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=28)

    def get(self, *args, **kwargs):
        all_engagements = Engagement.objects.all()
        assigned_engagements = Assignments.objects.values('engagement_id', 'engagement_id__srg_id',
                                                          'engagement_id__time_code',
                                                          'engagement_id__time_code__time_code_desc',
                                                          'engagement_id__provider_id', 'engagement_id__fye',
                                                          'engagement_id__provider_id__provider_name').annotate(
            ecount=Count('engagement_id'))

        unassigned_engagements = all_engagements.exclude(
            engagement_id__in=assigned_engagements.values_list('engagement_id', flat=True))

        current_todolist = Todolist.objects.all()

        context = {'today': self.today, 'week_beg': self.week_beg, 'week_end': self.week_end,
                   'assigned_engagements': assigned_engagements,
                   'all_engagements': all_engagements, 'unassigned_engagements': unassigned_engagements,
                   'current_todo_list': current_todolist}

        return self.render_to_response(context)


class Expenses(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    # redirect_field_name = ''
    template_name = 'expense.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):
        expense_entries = Expense.objects.filter(employee__user_id=self.request.user.id).filter(
            date__gte=self.week_beg).filter(
            date__lte=self.week_end)

        weekly_total = expense_entries.values().aggregate(weekly_expense_total=Sum('expense_amount'))

        add_time_form = TimeForm(self.request.POST)

        context = {'today': self.today, 'week_beg': self.week_beg,
                   'week_end': self.week_end, 'expense_entries': expense_entries,
                   'add_time_form': add_time_form, 'weekly_total': weekly_total}

        return self.render_to_response(context)


class TimesheetAdmin(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    # redirect_field_name = ''
    template_name = 'admin_timesheet.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):
        timesheet_entries = Time.objects.filter(
            date__gte=self.week_beg).filter(
            date__lte=self.week_end)

        weekly_total = timesheet_entries.values().aggregate(weekly_hours_total=Sum('hours'))

        add_time_form = TimeForm(self.request.POST)

        context = {'today': self.today, 'week_beg': self.week_beg,
                   'week_end': self.week_end, 'timesheet_entries': timesheet_entries,
                   'add_time_form': add_time_form, 'weekly_total': weekly_total}

        return self.render_to_response(context)


@login_required(login_url='/login')
def adminTS(request):
    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)

    queryset = Time.objects.values('date', 'employee__user__username', 'engagement__srg_id',
                                   'engagement__parent__parent_name', 'engagement__provider',
                                   'engagement__provider__provider_name', 'engagement__time_code',
                                   'engagement__time_code__time_code_desc', 'hours', 'note')

    f = TimesheetFilter(request.GET, queryset=queryset)

    if request.method == 'GET' and 'extract_button' in request.GET:
        ts_data = read_frame(f.qs)

        fname = 'EmployeeTimesheetCompilation'

        response = HttpResponse(content_type='application/vns.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=' + fname + '.xlsx'
        with pandas.ExcelWriter(response, engine='xlsxwriter') as writer:
            ts_data.to_excel(writer, sheet_name=('SRG Timesheet Compilation'), index=False, header=True)
            # df_hfy.to_excel(writer, sheet_name=('PFY ' + fye), index=False, header=True)

            return response

    context = {'filter': f, 'today': today, 'week_beg': week_beg, 'week_end': week_end}
    return render(request, 'admin_timesheet.html', context)
