# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField
from django.utils.safestring import mark_safe

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

course_choices = (('LinuxL', 'Linux中高级'),
                  ('PythonFullStack', 'Python高级全栈开发'),)

class_type_choices = (('fulltime', '脱产班',),
                      ('online', '网络班'),
                      ('weekend', '周末班',),)

source_type = (('qq', "qq群"),
               ('referral', "内部转介绍"),
               ('website', "官方网站"),
               ('baidu_ads', "百度推广"),
               ('office_direct', "直接上门"),
               ('WoM', "口碑"),
               ('public_class', "公开课"),
               ('website_luffy', "路飞官网"),
               ('others', "其它"),)

enroll_status_choices = (('signed', "已报名"),
                         ('unregistered', "未报名"),
                         ('studying', '学习中'),
                         ('paid_in_full', "学费已交齐"))

seek_status_choices = (('A', '近期无报名计划'), ('B', '1个月内报名'), ('C', '2周内报名'), ('D', '1周内报名'),
                       ('E', '定金'), ('F', '到班'), ('G', '全款'), ('H', '无效'),)
pay_type_choices = (('deposit', "订金/报名费"),
                    ('tuition', "学费"),
                    ('transfer', "转班"),
                    ('dropout', "退学"),
                    ('refund', "退款"),)

attendance_choices = (('checked', "已签到"),
                      ('vacate', "请假"),
                      ('late', "迟到"),
                      ('absence', "缺勤"),
                      ('leave_early', "早退"),)

score_choices = ((100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (70, 'B-'), (60, 'C+'), (50, 'C'), (40, 'C-'),
                 (0, ' D'), (-1, 'N/A'), (-100, 'COPY'), (-1000, 'FAIL'),)


class UserInfo(AbstractUser):
    """
    员工表
    """
    tel = models.CharField(max_length=32)
    gender = models.IntegerField(choices=((1, "男"), (2, "女")), default=1)
    depart = models.ForeignKey('Department',on_delete=models.CASCADE,default=1)


class Department(models.Model):
    """
    部门表
    """
    name=models.CharField(max_length=32)
    count=models.IntegerField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    客户表
    """
    qq = models.CharField('QQ', max_length=64, unique=True, help_text='QQ号必须唯一')
    qq_name = models.CharField('QQ昵称', max_length=64, blank=True, null=True)
    name = models.CharField('姓名', max_length=32, blank=True, null=True, help_text='学员报名后，请改为真实姓名')
    sex_type = (('male', '男'), ('female', '女'))
    sex = models.CharField("性别", choices=sex_type, max_length=16, default='male', blank=True, null=True)
    birthday = models.DateField('出生日期', default=None, help_text="格式yyyy-mm-dd", blank=True, null=True)
    phone = models.BigIntegerField('手机号', blank=True, null=True)
    source = models.CharField('客户来源', max_length=64, choices=source_type, default='qq')
    introduce_from = models.ForeignKey('Customer', verbose_name="转介绍自学员", blank=True, null=True,on_delete=models.CASCADE)
    course = MultiSelectField("咨询课程", choices=course_choices)
    class_type = models.CharField("班级类型", max_length=64, choices=class_type_choices, default='fulltime')
    customer_note = models.TextField("客户备注", blank=True, null=True, )
    status = models.CharField("状态", choices=enroll_status_choices, max_length=64, default="unregistered",
                              help_text="选择客户此时的状态")
    date = models.DateTimeField("咨询日期", auto_now_add=True)
    last_consult_date = models.DateField("最后跟进日期", auto_now_add=True)
    next_date = models.DateField("预计再次跟进时间", blank=True, null=True)
    consultant = models.ForeignKey('UserInfo', verbose_name="销售", related_name='customers', blank=True, null=True,on_delete=models.CASCADE )
    class_list = models.ManyToManyField('ClassList', verbose_name="已报班级", )
    deal_date = models.DateField(null=True)

    def __str__(self):
        return self.name + str(self.deal_date)

    def get_classlist(self):
        l = []
        for cls in self.class_list.all():
            l.append(str(cls))
        return mark_safe("<br>".join(l))

    def get_status(self):
        status_color = {
            "studying": "green",
            "signed": "#B03060",
            "unregistered": "red",
            "paid_in_full": "blue"
        }
        return mark_safe("<span style='color:%s;'>%s</span>" % (status_color[self.status], self.get_status_display()))


class Campuses(models.Model):
    """
    校区表
    """
    name = models.CharField(verbose_name='校区', max_length=64)
    address = models.CharField(verbose_name='详细地址', max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """
    班级表
    """
    course = models.CharField("课程名称", max_length=64, choices=course_choices)
    semester = models.IntegerField("学期")
    campuses = models.ForeignKey('Campuses', verbose_name="校区",on_delete=models.CASCADE)
    price = models.IntegerField("学费", default=10000)
    memo = models.CharField('说明', blank=True, null=True, max_length=100)
    start_date = models.DateField("开班日期")
    graduate_date = models.DateField("结业日期", blank=True, null=True)
    teachers = models.ManyToManyField('UserInfo', verbose_name="老师")
    class_type = models.CharField(choices=class_type_choices, max_length=64, verbose_name='班额及类型', blank=True,
                                  null=True)

    class Meta:
        unique_together = ("course", "semester", 'campuses')

    def __str__(self):
        return "{}{}({})".format(self.get_course_display(), self.semester, self.campuses)


class ConsultRecord(models.Model):
    """
    跟进记录表
    """
    customer = models.ForeignKey('Customer', verbose_name="所咨询客户",on_delete=models.CASCADE)
    note = models.TextField(verbose_name="跟进内容...")
    status = models.CharField("跟进状态", max_length=8, choices=seek_status_choices, help_text="选择客户此时的状态")
    consultant = models.ForeignKey("UserInfo", verbose_name="跟进人", related_name='records',on_delete=models.CASCADE)
    date = models.DateTimeField("跟进日期", auto_now_add=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)

    def __str__(self):
        return str(self.customer)+str(self.consultant)


class Enrollment(models.Model):
    """
    报名表
    """
    customer = models.ForeignKey('Customer', verbose_name='客户名称',on_delete=models.CASCADE)
    why_us = models.TextField("为什么报名", max_length=1024, default=None, blank=True, null=True)
    your_expectation = models.TextField("学完想达到的具体期望", max_length=1024, blank=True, null=True)
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name="报名日期")
    memo = models.TextField('备注', blank=True, null=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)
    school = models.ForeignKey('Campuses',on_delete=models.CASCADE)
    enrolment_class = models.ForeignKey("ClassList", verbose_name="所报班级",on_delete=models.CASCADE)

    class Meta:
        unique_together = ('enrolment_class', 'customer')


class PaymentRecord(models.Model):
    """
    缴费记录表
    """
    customer = models.ForeignKey('Customer', verbose_name="客户",on_delete=models.CASCADE)
    pay_type = models.CharField("费用类型", choices=pay_type_choices, max_length=64, default="deposit")
    paid_fee = models.IntegerField("费用数额", default=0)
    note = models.TextField("备注", blank=True, null=True)
    date = models.DateTimeField("交款日期", auto_now_add=True)
    course = models.CharField("课程名", choices=course_choices, max_length=64, blank=True, null=True, default='N/A')
    class_type = models.CharField("班级类型", choices=class_type_choices, max_length=64, blank=True, null=True,
                                  default='N/A')
    enrolment_class = models.ForeignKey('ClassList', verbose_name='所报班级', blank=True, null=True,on_delete=models.CASCADE)
    consultant = models.ForeignKey('UserInfo', verbose_name="销售",on_delete=models.CASCADE)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)

    status_choices = (
        (1, '未审核'),
        (2, '已审核'),
    )
    status = models.IntegerField(verbose_name='审核', default=1, choices=status_choices)

    confirm_date = models.DateTimeField(verbose_name="确认日期", null=True, blank=True)
    confirm_user = models.ForeignKey(verbose_name="确认人", to='UserInfo', related_name='confirms', null=True,
                                     blank=True,on_delete=models.CASCADE)


########################### 学员管理 #########################


class Student(models.Model):
    """
    学生表（已报名）
    """
    customer = models.OneToOneField(verbose_name='客户信息', to='Customer',on_delete=models.CASCADE,null=True,blank=True)
    class_list = models.ManyToManyField(verbose_name="已报班级", to='ClassList', blank=True,related_name="students")

    emergency_contract = models.CharField(max_length=32, blank=True, null=True, verbose_name='紧急联系人')
    company = models.CharField(verbose_name='公司', max_length=128, blank=True, null=True)
    location = models.CharField(max_length=64, verbose_name='所在区域', blank=True, null=True)
    position = models.CharField(verbose_name='岗位', max_length=64, blank=True, null=True)
    salary = models.IntegerField(verbose_name='薪资', blank=True, null=True)
    welfare = models.CharField(verbose_name='福利', max_length=256, blank=True, null=True)
    date = models.DateField(verbose_name='入职时间', help_text='格式yyyy-mm-dd', blank=True, null=True)
    memo = models.CharField(verbose_name='备注', max_length=256, blank=True, null=True)

    def __str__(self):
        return self.customer.name


class ClassStudyRecord(models.Model):
    """
    上课记录表 （班级记录）
    """
    class_obj = models.ForeignKey(verbose_name="班级", to="ClassList",on_delete=models.CASCADE)
    day_num = models.IntegerField(verbose_name="节次", help_text=u"此处填写第几节课或第几天课程...,必须为数字")

    teacher = models.ForeignKey(verbose_name="讲师", to='UserInfo',on_delete=models.CASCADE)
    date = models.DateField(verbose_name="上课日期", auto_now_add=True)
    course_title = models.CharField(verbose_name='本节课程标题', max_length=64, blank=True, null=True)
    course_memo = models.TextField(verbose_name='本节课程内容概要', blank=True, null=True)
    has_homework = models.BooleanField(default=True, verbose_name="本节有作业",blank=True)
    homework_title = models.CharField(verbose_name='本节作业标题', max_length=64, blank=True, null=True)
    homework_memo = models.TextField(verbose_name='作业描述', max_length=500, blank=True, null=True)
    exam = models.TextField(verbose_name='踩分点', max_length=300, blank=True, null=True)

    def __str__(self):
        return "{0} day{1}".format(self.class_obj, self.day_num)


class StudentStudyRecord(models.Model):
    """
    学生学习记录
    """
    student = models.ForeignKey(verbose_name="学员", to='Student',on_delete=models.CASCADE)
    classstudyrecord = models.ForeignKey(verbose_name="第几天课程", to="ClassStudyRecord",on_delete=models.CASCADE)
    record_choices = (('checked', "已签到"),
                      ('vacate', "请假"),
                      ('late', "迟到"),
                      ('noshow', "缺勤"),
                      ('leave_early', "早退"),
                      )
    record = models.CharField("上课纪录", choices=record_choices, default="checked", max_length=64)
    score_choices = ((100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (70, 'B-'),
                     (60, 'C+'),
                     (50, 'C'),
                     (40, 'C-'),
                     (0, ' D'),
                     (-1, 'N/A'),
                     (-100, 'COPY'),
                     (-1000, 'FAIL'),
                     )
    score = models.IntegerField("本节成绩", choices=score_choices, default=-1)
    homework_note = models.CharField(verbose_name='作业评语', max_length=255, blank=True, null=True)
    note = models.CharField(verbose_name="备注", max_length=255, blank=True, null=True)

    homework = models.FileField(verbose_name='作业文件', blank=True, null=True, default=None)
    stu_memo = models.TextField(verbose_name='学员备注', blank=True, null=True)
    date = models.DateTimeField(verbose_name='提交作业日期', auto_now_add=True)

    def __str__(self):
        return "{0}-{1}".format(self.classstudyrecord, self.student)

    class Meta:
        unique_together=["student","classstudyrecord"]