# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-23 05:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0006_auto_20191222_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='deal_date',
            field=models.DateField(null=True),
        ),
    ]
