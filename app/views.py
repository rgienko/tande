from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin

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


class Dashboard(LoginRequiredMixin, TemplateView):
    login_url = 'localhost:8000/login'
    redirect_field_name = 'dashboard/'
    template_name = 'dashboard.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):
        add_time_form = TimeForm(self.request.POST)
        all_engagements = Engagement.objects.all()
        for engagement in all_engagements:
            if self.request.user.is_staff:

                engagement_time_sheet_entries = Time.objects.filter(engagement=engagement.engagement_id)
            else:
                engagement_time_sheet_entries = Time.objects.filter(engagement=engagement.engagement_id).filter(
                    employee=self.request.user.id)

            engagement_time_sheet_by_employee = engagement_time_sheet_entries.values('employee__user__username',
                                                                                     'employee__rate').annotate(
                engagement_emp_hours=Sum('hours')).order_by('-engagement_emp_hours')

            engagement.staff = Assignments.objects.filter(engagement=engagement.engagement_id)

            engagement.engagement_time_sheet_entries = engagement_time_sheet_by_employee

            engagement_total_hours = engagement_time_sheet_entries.aggregate(
                project_hours=Sum('hours'))

            engagement.engagement_hours = engagement_total_hours

        context = {'all_engagements': all_engagements, 'add_time_form': add_time_form}

        return self.render_to_response(context)

    # noinspection DuplicatedCode
    def post(self, *args, **kwargs):
        # noinspection DuplicatedCode
        add_time_form = TimeForm(self.request.POST)
        engagement_id = self.request.POST.get('engagement-input')

        engagement_instance = get_object_or_404(Engagement, srg_id=engagement_id)
        employee_instance = get_object_or_404(Employee, pk=self.request.user.id)

        if add_time_form.is_valid():
            new_entry = add_time_form.save(commit=False)
            new_entry.employee = employee_instance
            # new_entry.date = self.today
            new_entry.engagement = engagement_instance
            new_entry.save()
            return redirect(reverse_lazy('dashboard'))

        context = {'add_time_form': add_time_form}

        return self.render_to_response(context)


class Timesheet(TemplateView):
    template_name = 'timesheet.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=5)
    thirty = date.today() - timedelta(days=30)

    def get(self, *args, **kwargs):
        timesheet_entries = Time.objects.filter(employee=self.request.user.id).filter(date__gte=self.week_beg).filter(
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
        employee_instance = get_object_or_404(Employee, pk=self.request.user.id)

        if add_time_form.is_valid():
            new_entry = add_time_form.save(commit=False)
            new_entry.employee = employee_instance
            new_entry.engagement = engagement_instance
            new_entry.save()
            return redirect(reverse_lazy('timesheet'))

        context = {'add_time_form': add_time_form}

        return self.render_to_response(context)


class TodolistView(TemplateView):
    template_name = 'todolist.html'

    today = date.today()
    week_beg = today - timedelta(days=today.weekday())
    week_end = week_beg + timedelta(days=28)

    def get(self, *args, **kwargs):
        assigned_engagements = Assignments.objects.select_related('engagement').filter(assignee=self.request.user.id)
        current_todolist = Todolist.objects.filter(employee=self.request.user.id)
        add_todo_form = TodoForm(self.request.POST)

        context = {'today': self.today, 'week_beg': self.week_beg, 'week_end': self.week_end,
                   'assigned_engagements': assigned_engagements, 'add_todo_form': add_todo_form,
                   'current_todo_list': current_todolist}

        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        engagement_id = self.request.POST.get('engagement-input')
        engagement_instance = get_object_or_404(Engagement, srg_id=engagement_id)
        employee_instance = get_object_or_404(Employee, pk=self.request.user.id)

        add_todo_form = TodoForm(self.request.POST)

        if add_todo_form.is_valid():
            new_entry = add_todo_form.save(commit=False)
            new_entry.employee = employee_instance
            new_entry.engagement = engagement_instance
            new_entry.save()
            return redirect(reverse_lazy('todolist'))

        context = {'add_todo_form': add_todo_form}

        return self.render_to_response(context)


def createEngagement(request):
    if request.method == 'POST':

        form = EngagementForm(request.POST)

        who = request.POST.get('provider')
        what = request.POST.get('time_code')
        when = request.POST.get('fye')
        when = when[:4]
        how = request.POST.get('type')
        srgid = who + "." + str(what) + "." + str(
            when) + "." + how

        if form.is_valid():
            new_engagement = form.save(commit=False)
            new_engagement.srg_id = srgid
            new_engagement.save()

            return redirect('add-assignments', new_engagement.engagement_id)

    else:
        form = EngagementForm()

    context = {'form': form}

    return render(request, 'create_engagement.html', context)


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


def engagementDashboard(request):
    all_engagements = Engagement.objects.all()

    context = {'all_engagements': all_engagements}
    return render(request, 'engagements.html', context)
