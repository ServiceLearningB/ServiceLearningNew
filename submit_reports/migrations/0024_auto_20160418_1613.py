# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-18 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submit_reports', '0023_auto_20160418_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submitreport',
            name='courses',
            field=models.ManyToManyField(null=True, to='submit_reports.Course'),
        ),
    ]