# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-16 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='gender',
            field=models.IntegerField(choices=[(1, '\u7537'), (2, '\u5973')], default=1),
        ),
    ]
