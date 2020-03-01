# -*- coding: utf-8 -*-
"""crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from app01 import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.login),  # 登录
    url(r'^get_valid_img/$', views.get_valid_img),  # 验证码
    url(r'^reg/$', views.reg),  # 注册
    url(r'^logout/$', views.logout),  # 退出
    url(r'^index/$', views.index),  # 主页
    url(r'^$', views.index),
    # 公户
    url(r'^customers/public/$', views.CustomerView.as_view(),name="customers_public"),
    # 全部列表
    url(r'^customers/list/$', views.CustomerView.as_view(),name="customers_list"),
    # 个人账户
    url(r'^mycustomers/$', views.CustomerView.as_view(),name="mycustomers"),
    # url(r'^customer/add/$', views.AddCustomerView.as_view(), name='addcustomers'),
    # url(r'^customer/edit/(\d+)/$', views.EditCustomerView.as_view(),name="editcustomers"),
    # 添加客户
    url(r'^customer/add/$', views.AddEditCustomerView.as_view(), name='addcustomers'),
    # 编辑客户
    url(r'^customer/edit/(\d+)/$', views.AddEditCustomerView.as_view(),name="editcustomers"),
    # 查看详情记录
    url(r'^consult_records/$', views.ConsultRecordsView.as_view(), name='consultrecords'),
    # 添加详情记录
    url(r'^consult_records/add/$', views.AddEditConsultRecordView.as_view(), name="add_consult_records"),
    # 编辑详情记录
    url(r'^consult_records/edit/(\d+)/$', views.AddEditConsultRecordView.as_view(), name="edit_consult_records"),
    # 班级学习记录
    url(r'^class_study_record/$', views.ClassStudyRecordView.as_view(), name="class_study_record"),
    # 记录分数
    url(r'^record_score/(\d+)/$', views.RecordScoreView.as_view(), name="record_score"),
    # 成单统计
    url(r'^customer/tongji/$', views.TongJiView.as_view(), name="tongji"),
    url(r'^rbac/', include('rbac.urls'))
]
