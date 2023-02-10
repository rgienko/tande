from datetime import date

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Type(models.Model):
    type_id = models.CharField(max_length=1, primary_key=True)
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=40)
    rate = models.IntegerField()


class Parent(models.Model):
    parent_id = models.CharField(max_length=15, primary_key=True)
    parent_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['parent_id']

    def __str__(self):
        return self.parent_id+"-"+self.parent_name


class Provider(models.Model):
    provider_id = models.CharField(max_length=6, primary_key=True)
    provider_name = models.CharField(max_length=100)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)

    class Meta:
        ordering = ['provider_id']

    def __str__(self):
        return self.provider_id + "-" + self.provider_name


class Timecode(models.Model):
    time_code = models.IntegerField(primary_key=True, null=False, blank=False)
    time_code_desc = models.TextField(max_length=75, null=True, blank=True)
    time_code_hours = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['time_code']

    def __str__(self):
        return str(self.time_code) + "-" + self.time_code_desc


class Engagement(models.Model):
    engagement_id = models.AutoField(primary_key=True)
    srg_id = models.CharField(max_length=20)
    start_date = models.DateField()
    # target_end_date = models.DateField()
    fye = models.DateField(null=True, blank=True)
    budget_amount = models.IntegerField(null=True, default=10000)
    budget_hours = models.IntegerField(default=120)
    is_complete = models.BooleanField(default=False)
    complete_date = models.DateField(blank=True, default=date.today)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    time_code = models.ForeignKey(Timecode, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return self.srg_id

    def getProviderName(self):
        return self.provider.provider_name

    def getParentName(self):
        return self.parent.parent_name


class Assignments(models.Model):
    assignment_id = models.AutoField(primary_key=True, blank=False, null=False)
    engagement = models.ForeignKey(Engagement, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.engagement.srg_id
