# -*- coding: utf-8 -*-
'''
dasist.scan.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = (
    # 'scan.views',
    url(r'^$',                  login_required(views.ScanList.as_view()), name='scan_list'),
    url(r'^lpp/(?P<lpp>\d+)/$', views.scan_set_lpp),
    url(r'^filter/$',           views.scan_set_filter),
    url(r'^get_subjs/$',        views.scan_get_subjects),
    # url(r'^a/$',              views.scan_add),
    url(r'^(?P<pk>\d+)/$',      login_required(views.ScanDetail.as_view()), name='scan_view'),
    url(r'^(?P<id>\d+)/u/$',    views.scan_edit),
    url(r'^(?P<id>\d+)/d/$',    views.scan_delete),
    url(r'^clean_spaces/$',     views.scan_clean_spaces),
    url(r'^replace_depart/$',   views.scan_replace_depart),
    url(r'^replace_place/$',    views.scan_replace_place),
)
