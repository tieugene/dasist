# -*- coding: utf-8 -*-
'''
dasist.scan.urls
'''

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import views

urlpatterns = patterns('scan.views',
	#url(r'^$',			'scan_list'),
	url(r'^$',			login_required(views.ScanList.as_view()), name='scan_list'),
	url(r'^lpp/(?P<lpp>\d+)/$',	'scan_set_lpp'),
	#url(r'^a/$',			'scan_add'),
	#url(r'^(?P<id>\d+)/$',		'scan_view'),
	url(r'^(?P<pk>\d+)/$',		login_required(views.ScanDetail.as_view()), name='scan_view'),
	url(r'^(?P<id>\d+)/u/$',	'scan_edit'),
	url(r'^(?P<id>\d+)/d/$',	'scan_delete'),
	url(r'^clean_spaces/$',		'scan_clean_spaces'),
	url(r'^replace_depart/$',	'scan_replace_depart'),
	url(r'^replace_place/$',	'scan_replace_place'),
)
