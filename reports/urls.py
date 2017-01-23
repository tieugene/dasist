# -*- coding: utf-8 -*-
'''
dasist.reports.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

import views

urlpatterns = (
    url(r'^ledger/$',                               login_required(views.LedgerList.as_view()), name='ledger_list'),
    url(r'^ledger/lpp/(?P<lpp>\d+)/$',              views.ledger_set_lpp, name='ledger_set_lpp'),
    url(r'^ledger/filter/$',                        views.ledger_set_filter, name='ledger_set_filter'),
    url(r'^summary/$',                              login_required(views.SummaryList.as_view()), name='summary_list'),
    url(r'^summary/filter/$',                       views.summary_set_filter, name='summary_set_filter'),
    # url(r'^summary/(?P<y>\d+)/(?P<place>\w+)/$',    views.summary_detail, name='summary_detail'),
    # url(r'^summary/(?P<p>\d+)/(?P<y>\d+)/$',        views.summary_detail, name='summary_detail'),
)
