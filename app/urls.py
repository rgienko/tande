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

from app import views

urlpatterns = [
    path("login/", views.login, name='login'),
    path("register/", views.register, name='register'),
    path("dashboard/", views.Dashboard.as_view(), name='dashboard'),
    path("timesheet/", views.Timesheet.as_view(), name='timesheet'),
    path("expense/", views.Expenses.as_view(), name='expense'),
    path("timesheet/edit/<pk>/", views.editTimesheet, name='edit-timesheet'),
    path("todolist/", views.TodolistView.as_view(), name='todolist'),
    path("todolist_admin/", views.TodolistViewAdmin.as_view(), name='admin-todolist'),
    path("timesheet_admin/", views.TimesheetAdmin.as_view(), name='admin-timesheet'),
    path("create-engagement/", views.createEngagement, name='create-engagement'),
    path("add-assignments/<pk>/", views.createAssignments, name='add-assignments'),
    path("dashboard/engagements/", views.EngagementDashboard.as_view(), name='dashboard-engagements'),

]
