# Generated by Django 5.2 on 2025-04-03 18:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('roll_number', models.CharField(max_length=10, unique=True)),
                ('year', models.CharField(max_length=10)),
                ('attendance', models.JSONField(default=dict)),
            ],
            options={
                'db_table': 'student_it_2nd_year',
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('is_present', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='home.student')),
            ],
        ),
    ]
