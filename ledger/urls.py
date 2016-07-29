# -*- coding: utf-8 -*-
'''
dasist.ledger.urls
'''

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import views

urlpatterns = patterns('ledger.views',
	url(r'^$',			login_required(views.LedgerList.as_view()), name='ledger_list'),
	url(r'^lpp/(?P<lpp>\d+)/$',	'ledger_set_lpp'),
	url(r'^filter/$',		'ledger_set_filter'),
)
