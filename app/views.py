from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages

from .forms import *

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


def dashboard(request):
    return render(request, 'layout.html')


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

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            new_assignment = form.save(commit=False)
            new_assignment.save()

            return redirect(dashboard)

    else:

        form = AssignmentForm(initial={'engagement': srgid})

    context = {'engagement_instance': engagement_instance, 'form': form}

    return render(request, 'create_assignments.html', context)


def engagementDashboard(request):
    all_engagements = Engagement.objects.all()

    context = {'all_engagements': all_engagements}
    return render(request, 'engagements.html', context)
