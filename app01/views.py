# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, HttpResponse, redirect
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.contrib import auth
from django.http import JsonResponse
from app01.models import UserInfo, Customer, ConsultRecord, ClassStudyRecord, StudentStudyRecord
from django.urls import reverse
from django.db.models import Q
from app01.utils.form import UserForm, CustomerModelForm
from app01.utils.page import Pagination
from django.contrib.auth.decorators import login_required
from django.views import View
from django import forms
from multiselectfield import MultiSelectField
from django.forms.models import modelformset_factory
from django.db.models import Count
import random
import datetime


def login(request):
    """
    基于ajax和用户认证组件实现的登录功能
    """
    # if request.method == 'POST':
    if request.is_ajax():
        # Ajax请求返回一个字典
        response = {"user": None, "err_msg": ""}
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        validcode = request.POST.get('validcode')
        if validcode.upper() == request.session.get('keep_str').upper():
            user_obj = auth.authenticate(username=user, password=pwd)
            if user_obj:
                auth.login(request, user_obj)  # request.session["user_id"]=user_obj.pk
                response['user'] = user
            else:
                response['err_msg'] = '用户名或者密码错误！'
        else:
            response['err_msg'] = '验证码错误！'
        return JsonResponse(response)
    else:
        return render(request, 'login.html')


def get_valid_img(request):  # 制作验证码
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    img = Image.new('RGB', (200, 35), 'gray')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('static/ARIBLK.TTF', 32)
    keep_str = ''
    for i in range(4):
        random_num = str(random.randint(0, 9))
        random_lowalf = chr(random.randint(97, 122))
        random_upperalf = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_lowalf, random_upperalf])
        draw.text((i * 40 + 30, 0), random_char, (get_random_color()), font=font)
        keep_str += random_char

    # 写与读
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()

    # 将验证码存在各自的session中
    request.session['keep_str'] = keep_str
    return HttpResponse(data)


def reg(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        res = {'user': None, 'err_msg': ''}
        if form.is_valid():
            res['user'] = form.cleaned_data.get('user')
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            user = UserInfo.objects.create_user(username=user, password=pwd, email=email, gender=gender)
        else:
            res['err_msg'] = form.errors
        return JsonResponse(res)
    else:
        form = UserForm()
        return render(request, 'reg.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('/login/')


# @login_required
def index(request):
    return render(request, 'index.html')


# @login_required
# def customers(request):
#     if reverse('customers_list') == request.path:
#         customer_list = Customer.objects.all()
#     else:
#         customer_list = Customer.objects.filter(consultant=request.user)
#
#     # search过滤
#     val = request.GET.get("q")
#     select = request.GET.get('select')
#     # filter_field = "name"
#     if val:
#         q = Q()
#         q.connector = 'or'
#         q.children.append((select+'__contains',val))
#
#         customer_list = customer_list.filter(q)
#
#         # customer_list=customer_list.filter(Q(name__contains=val)|Q(qq__contains=val))
#
#     # 分页
#     current_page_num = request.GET.get("page")
#     pagination = Pagination(current_page_num, customer_list.count(), request)
#
#     customer_list = customer_list[pagination.start:pagination.end]
#
#     return render(request, "customer_list.html", {"customer_list": customer_list, "pagination": pagination})


class CustomerView(View):
    def get(self, request):
        if reverse('customers_public') == request.path:
            label = "公户列表"
            customer_list = Customer.objects.filter(consultant__isnull=True)  # 没有销售
        elif reverse('customers_list') == request.path:
            label = '全部客户'
            customer_list = Customer.objects.all()
        else:
            label = "我的客户"
            customer_list = Customer.objects.filter(consultant=request.user)

        # search过滤
        val = request.GET.get("q")
        select = request.GET.get('select')
        # filter_field = "name"
        if val:
            q = Q()
            q.connector = 'or'
            q.children.append((select + '__contains', val))

            customer_list = customer_list.filter(q)

            # customer_list=customer_list.filter(Q(name__contains=val)|Q(qq__contains=val))

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, customer_list.count(), request)

        customer_list = customer_list[pagination.start:pagination.end]

        path = request.path
        next = "?next=%s" % path

        return render(request, "customer/customer_list.html", {"customer_list": customer_list, "pagination": pagination,
                                                               'label': label, 'next': next})

    def post(self, request):
        # action的批量处理
        func_str = request.POST.get('action')
        data = request.POST.getlist('selected_pk_list')
        if not hasattr(self, func_str):
            return HttpResponse("非法输入！")
        else:
            func = getattr(self, func_str)
            queryset = Customer.objects.filter(pk__in=data)
            ret = func(request, queryset)
            if ret:
                return ret
            # ret=self.get(request)
            # return ret
            return redirect(request.path)

    def patch_delete(self, request, queryset):
        queryset.delete()
        # queryset.update(sex='male')

    def patch_reverse_gs(self, request, queryset):
        '''
        公户转私户
        :param data:
        :return:
        '''
        # queryset.update(consultant=request.user)
        ret = queryset.filter(consultant__isnull=True)
        if ret:
            ret.update(consultant=request.user)
        else:
            return HttpResponse("手速太慢！")

    def patch_reverse_sg(self, request, queryset):
        '''
        私户转公户
        :param data:
        :return:
        '''
        queryset.update(consultant=None)


# class AddCustomerView(View):
#     def get(self, request):
#         forms = CustomerModelForm()
#         return render(request, 'add_customer.html', {'forms':forms})
#
#     def post(self, request):
#         forms = CustomerModelForm(request.POST)
#         if forms.is_valid():
#             forms.save()
#             return redirect(reverse('customers_list'))
#         else:
#             return render(request, 'add_customer.html', {'forms':forms})
#
#
# class EditCustomerView(View):
#     def get(self, request, id):
#         edit_obj = Customer.objects.filter(pk=id).first()
#         forms = CustomerModelForm(instance=edit_obj)
#         return render(request, 'edit_customer.html', {'forms':forms})
#
#     def post(self, request, id):
#         edit_obj = Customer.objects.filter(pk=id).first()
#         forms = CustomerModelForm(request.POST, instance=edit_obj)
#         if forms.is_valid():
#             forms.save()
#             return redirect(request.GET.get('next'))
#         else:
#             return render(request, 'edit_customer.html', {'forms':forms})

# 添加和编辑客户
class AddEditCustomerView(View):
    def get(self, request, edit_id=None):
        edit_obj = Customer.objects.filter(pk=edit_id).first()
        form = CustomerModelForm(instance=edit_obj)
        return render(request, 'customer/add_edit_customer.html', {'form': form, 'edit_obj': edit_obj})

    def post(self, request, edit_id=None):
        edit_obj = Customer.objects.filter(pk=edit_id).first()
        form = CustomerModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(request.GET.get('next'))
        else:
            return render(request, 'customer/add_edit_customer.html', {'form': form, 'edit_obj': edit_obj})


class ConsultRecordModelForm(forms.ModelForm):
    class Meta:
        model = ConsultRecord
        # fields="__all__"
        exclude = ["delete_status"]


# 添加和编辑详情记录
class AddEditConsultRecordView(View):
    def get(self, request, edit_id=None):
        edit_obj = ConsultRecord.objects.filter(pk=edit_id).first()
        form = ConsultRecordModelForm(instance=edit_obj)
        return render(request, "customer/add_edit_consultrecord.html", {"form": form, "edit_obj": edit_obj})

    def post(self, request, edit_id=None):
        edit_obj = ConsultRecord.objects.filter(pk=edit_id).first()
        form = ConsultRecordModelForm(request.POST, instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse("consultrecords"))
        else:
            return render(request, "customer/add_edit_consultrecord.html", {"form": form, "edit_obj": edit_obj})


class ConsultRecordsView(View):
    def get(self, request):
        consult_record_list = ConsultRecord.objects.filter(consultant=request.user)
        customer_id = request.GET.get("customer_id")
        if customer_id:
            consult_record_list = consult_record_list.filter(customer_id=customer_id)
        return render(request, "customer/consultrecord.html", {"consult_record_list": consult_record_list})


# 班级学习记录
class ClassStudyRecordView(View):
    def get(self, request):
        cls_study_record_list = ClassStudyRecord.objects.all()
        return render(request, 'student/class_study_record.html', locals())

    def post(self, request):
        action = request.POST.get('action')
        selected_pk_list = request.POST.getlist('selected_pk_list')
        if hasattr(self, action):
            getattr(self, action)(selected_pk_list)
        return self.get(request)

    def patch_init(self, selected_pk_list):
        # 批量创建学生学习记录
        try:
            for class_study_record_pk in selected_pk_list:
                class_study_record_obj = ClassStudyRecord.objects.filter(pk=class_study_record_pk).first()
                student_list = class_study_record_obj.class_obj.students.all()

                for student in student_list:
                    StudentStudyRecord.objects.create(student=student, classstudyrecord=class_study_record_obj)
        except Exception as e:
            pass


class RecordScoreView2(View):
    def get(self, request, class_study_record_id):
        class_study_record_obj = ClassStudyRecord.objects.get(pk=class_study_record_id)
        student_study_record_list = class_study_record_obj.studentstudyrecord_set.all()
        score_choices = StudentStudyRecord.score_choices
        return render(request, 'student/record_score.html', locals())

    def post(self, request, class_study_record_id):
        data_dict = {}
        for key, val in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue
            field, pk = key.rsplit('_', 1)
            if pk not in data_dict:
                data_dict[pk] = {
                    field: val
                }
            else:
                data_dict[pk][field] = val

        for pk, data in data_dict.items():
            StudentStudyRecord.objects.filter(pk=pk).update(**data)
            # StudentStudyRecord.objects.filter(pk=pk).update(**{field:val})

        return redirect(request.path)


class StudentStudyRecordModelForm(forms.ModelForm):
    class Meta:
        model = StudentStudyRecord
        fields = ["score", "homework_note"]


class RecordScoreView(View):
    def get(self, request, class_study_record_id):
        model_formset_cls = modelformset_factory(model=StudentStudyRecord, form=StudentStudyRecordModelForm, extra=0)
        queryset = StudentStudyRecord.objects.filter(classstudyrecord=class_study_record_id)
        formset = model_formset_cls(queryset=queryset)
        return render(request, "student/record_score.html", locals())

    def post(self, request, class_study_record_id):
        model_formset_cls = modelformset_factory(model=StudentStudyRecord, form=StudentStudyRecordModelForm, extra=0)
        # queryset = StudentStudyRecord.objects.filter(classstudyrecord=class_study_record_id)
        # print("request.POST",request.POST)
        formset = model_formset_cls(request.POST)
        if formset.is_valid():
            formset.save()

        # print(formset.errors)

        return redirect(request.path)


class TongJiView2(View):
    def get(self, request):
        date = request.GET.get('date', 'today')
        if hasattr(self, date):
            context = getattr(self, date)()
        return render(request, 'customer/tongji.html', context)

    def today(self):
        today = datetime.datetime.now().date()
        customer_list = Customer.objects.filter(deal_date=today)

        # 查询每一个销售的名字以及今天对应的成单量
        # select app01_userinfo.username, count(1) from app01_userinfo inner join app01_customer on app01_userinfo.id=app01_customer.consultant_id
        # where depart_id=1 and app01_customer.deal_date = '2019-12-23' group by app01_userinfo.id
        ret = UserInfo.objects.filter(depart_id=1, customers__deal_date=today).annotate(
            c=Count("customers")).values_list("username", "c")

        ret = [[item[0].encode('utf-8'), item[1]] for item in list(ret)]
        print(ret)
        return {'customer_list': customer_list, 'ret': list(ret)}

    def zuotian(self):
        zuotian = datetime.datetime.now().date() - datetime.timedelta(days=1)
        customer_list = Customer.objects.filter(deal_date=zuotian)
        return {'customer_list': customer_list}

    def week(self):
        today = datetime.datetime.now().date()
        week = datetime.datetime.now().date() - datetime.timedelta(weeks=1)
        customer_list = Customer.objects.filter(deal_date__gte=week, deal_date__lte=today)
        return {'customer_list': customer_list}

    def recent_month(self):
        today = datetime.datetime.now().date()
        month = datetime.datetime.now().date() - datetime.timedelta(weeks=4)
        customer_list = Customer.objects.filter(deal_date__gte=month, deal_date__lte=today)
        return {'customer_list': customer_list}


class TongJiView(View):
    def get(self, request):
        date = request.GET.get("date", "today")
        # func=getattr(self,date)
        # ret=func()
        today = datetime.datetime.now().date()
        delta1 = datetime.timedelta(days=1)
        delta2 = datetime.timedelta(weeks=1)
        delta3 = datetime.timedelta(weeks=4)

        condition = {
            "today": [{"deal_date": today}, {"customers__deal_date": today}],
            "zuotian": [{"deal_date": today - delta1}, {"customers__deal_date": today - delta1}],
            "week": [{"deal_date__gte": today - delta2, "deal_date__lte": today},
                     {"customers__deal_date__gte": today - delta2, "customers__deal_date__lte": today}
                     ],
            "recent_month": [{"deal_date__gte": today - delta3, "deal_date__lte": today},
                             {"customers__deal_date__gte": today - delta3, "customers__deal_date__lte": today}
                             ],
        }

        customer_list = Customer.objects.filter(**(condition.get(date)[0]))
        ret = UserInfo.objects.all().filter(**(condition.get(date)[1])).annotate(c=Count("customers")).values_list(
            "username", "c")
        ret = [[item[0].encode('utf-8'), item[1]] for item in list(ret)]

        return render(request, "customer/tongji.html", locals())
