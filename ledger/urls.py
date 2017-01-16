# -*- coding: utf-8 -*-
'''
dasist.ledger.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = (
    url(r'^$',                  login_required(views.LedgerList.as_view()), name='ledger_list'),
    url(r'^lpp/(?P<lpp>\d+)/$', views.ledger_set_lpp, name='ledger_set_lpp'),
    url(r'^filter/$',           views.ledger_set_filter, name='ledger_set_filter'),
)
