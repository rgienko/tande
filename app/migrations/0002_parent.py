# Generated by Django 4.1.6 on 2023-02-09 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Parent",
            fields=[
                (
                    "parent_id",
                    models.CharField(max_length=15, primary_key=True, serialize=False),
                ),
                ("parent_name", models.CharField(max_length=100)),
            ],
            options={"ordering": ["parent_id"],},
        ),
    ]
