# -*- coding: utf-8 -*-
'''
lansite.apps.core.urls
'''

from django.conf.urls.defaults import *

urlpatterns = patterns('scan.views',
	url(r'^$',			'scan_list'),
	url(r'^lpp/(?P<lpp>\d+)/$',	'scan_set_lpp'),
	url(r'^a/$',			'scan_add'),
	url(r'^(?P<id>\d+)/$',		'scan_view'),
	url(r'^(?P<id>\d+)/u/$',	'scan_edit'),
	url(r'^(?P<id>\d+)/d/$',	'scan_delete'),
)
