# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-12-22 10:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_auto_20191218_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassStudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_num', models.IntegerField(help_text='\u6b64\u5904\u586b\u5199\u7b2c\u51e0\u8282\u8bfe\u6216\u7b2c\u51e0\u5929\u8bfe\u7a0b...,\u5fc5\u987b\u4e3a\u6570\u5b57', verbose_name='\u8282\u6b21')),
                ('date', models.DateField(auto_now_add=True, verbose_name='\u4e0a\u8bfe\u65e5\u671f')),
                ('course_title', models.CharField(blank=True, max_length=64, null=True, verbose_name='\u672c\u8282\u8bfe\u7a0b\u6807\u9898')),
                ('course_memo', models.TextField(blank=True, null=True, verbose_name='\u672c\u8282\u8bfe\u7a0b\u5185\u5bb9\u6982\u8981')),
                ('has_homework', models.BooleanField(default=True, verbose_name='\u672c\u8282\u6709\u4f5c\u4e1a')),
                ('homework_title', models.CharField(blank=True, max_length=64, null=True, verbose_name='\u672c\u8282\u4f5c\u4e1a\u6807\u9898')),
                ('homework_memo', models.TextField(blank=True, max_length=500, null=True, verbose_name='\u4f5c\u4e1a\u63cf\u8ff0')),
                ('exam', models.TextField(blank=True, max_length=300, null=True, verbose_name='\u8e29\u5206\u70b9')),
                ('class_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.ClassList', verbose_name='\u73ed\u7ea7')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u8bb2\u5e08')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emergency_contract', models.CharField(blank=True, max_length=32, null=True, verbose_name='\u7d27\u6025\u8054\u7cfb\u4eba')),
                ('company', models.CharField(blank=True, max_length=128, null=True, verbose_name='\u516c\u53f8')),
                ('location', models.CharField(blank=True, max_length=64, null=True, verbose_name='\u6240\u5728\u533a\u57df')),
                ('position', models.CharField(blank=True, max_length=64, null=True, verbose_name='\u5c97\u4f4d')),
                ('salary', models.IntegerField(blank=True, null=True, verbose_name='\u85aa\u8d44')),
                ('welfare', models.CharField(blank=True, max_length=256, null=True, verbose_name='\u798f\u5229')),
                ('date', models.DateField(blank=True, help_text='\u683c\u5f0fyyyy-mm-dd', null=True, verbose_name='\u5165\u804c\u65f6\u95f4')),
                ('memo', models.CharField(blank=True, max_length=256, null=True, verbose_name='\u5907\u6ce8')),
                ('class_list', models.ManyToManyField(blank=True, related_name='students', to='app01.ClassList', verbose_name='\u5df2\u62a5\u73ed\u7ea7')),
                ('customer', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.Customer', verbose_name='\u5ba2\u6237\u4fe1\u606f')),
            ],
        ),
        migrations.CreateModel(
            name='StudentStudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.CharField(choices=[('checked', '\u5df2\u7b7e\u5230'), ('vacate', '\u8bf7\u5047'), ('late', '\u8fdf\u5230'), ('noshow', '\u7f3a\u52e4'), ('leave_early', '\u65e9\u9000')], default='checked', max_length=64, verbose_name='\u4e0a\u8bfe\u7eaa\u5f55')),
                ('score', models.IntegerField(choices=[(100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (70, 'B-'), (60, 'C+'), (50, 'C'), (40, 'C-'), (0, ' D'), (-1, 'N/A'), (-100, 'COPY'), (-1000, 'FAIL')], default=-1, verbose_name='\u672c\u8282\u6210\u7ee9')),
                ('homework_note', models.CharField(blank=True, max_length=255, null=True, verbose_name='\u4f5c\u4e1a\u8bc4\u8bed')),
                ('note', models.CharField(blank=True, max_length=255, null=True, verbose_name='\u5907\u6ce8')),
                ('homework', models.FileField(blank=True, default=None, null=True, upload_to=b'', verbose_name='\u4f5c\u4e1a\u6587\u4ef6')),
                ('stu_memo', models.TextField(blank=True, null=True, verbose_name='\u5b66\u5458\u5907\u6ce8')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='\u63d0\u4ea4\u4f5c\u4e1a\u65e5\u671f')),
                ('classstudyrecord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.ClassStudyRecord', verbose_name='\u7b2c\u51e0\u5929\u8bfe\u7a0b')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Student', verbose_name='\u5b66\u5458')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='studentstudyrecord',
            unique_together=set([('student', 'classstudyrecord')]),
        ),
    ]
