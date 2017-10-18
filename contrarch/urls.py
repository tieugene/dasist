# -*- coding: utf-8 -*-
'''
dasist.contrarch.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = (
    # 'contrarch.views',
    url(r'^$',                  login_required(views.ContrarchList.as_view()), name='contrarch_list'),
    url(r'^(?P<pk>\d+)/$',      login_required(views.ContrarchDetail.as_view()), name='contrarch_view'),
    url(r'^lpp/(?P<lpp>\d+)/$', views.contrarch_set_lpp, name='contrarch_set_lpp'),
    url(r'^filter/$',           views.contrarch_set_filter, name='contrarch_set_filter'),
    url(r'^get_subjs/$',        views.contrarch_get_subjects, name='contrarch_get_subjects'),
)
