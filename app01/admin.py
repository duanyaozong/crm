# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from app01.models import *

admin.site.register(UserInfo)
admin.site.register(ClassList)
admin.site.register(Customer)
admin.site.register(Campuses)
admin.site.register(ConsultRecord)
admin.site.register(Department)
admin.site.register(Student)
admin.site.register(ClassStudyRecord)
admin.site.register(StudentStudyRecord)
