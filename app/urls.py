"""tande URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from app import views

urlpatterns = [
    path("login/", views.login, name='login'),
    path("logout/", auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path("register/", views.register, name='register'),
    path("reset-password/", views.resetPassword, name='reset-password'),
    path("reset-password/done", views.resetPassword, name='reset-password'),
    path("dashboard/", views.Dashboard.as_view(), name='dashboard'),
    path("dashboard_admin/", views.AdminDashboard.as_view(), name='admin-dashboard'),
    path("admin_engagement_detail/<pk>/", views.AdminEngagementDetail, name='admin-engagement-detail'),
    path("timesheet/", views.Timesheet.as_view(), name='timesheet'),
    path("expense/", views.Expenses.as_view(), name='expense'),
    path("timesheet/edit/<pk>/", views.editTimesheet, name='edit-timesheet'),
    path("todolist/", views.TodolistView.as_view(), name='todolist'),
    path("todolist_admin/", views.TodolistViewAdmin.as_view(), name='admin-todolist'),
    path("timesheet_admin/", views.adminTS, name='admin-timesheet'),
    path("create-engagement/", views.createEngagement, name='create-engagement'),
    path("add-assignments/<pk>/", views.createAssignments, name='add-assignments'),
    path("dashboard/engagements/", views.EngagementDashboard.as_view(), name='dashboard-engagements'),
    path("timecodes/", views.timeCodes, name='timecodes'),
    path("timecodes/edit/<pk>/", views.editTimeCode, name='edit-timecode'),
    path("timecodes/new/", views.newTimeCode, name='new-timecode'),

]
