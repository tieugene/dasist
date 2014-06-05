# -*- coding: utf-8 -*-
'''
'''

from django.conf.urls.defaults import *

urlpatterns = patterns('addon.views',
	url(r'^$',			'addon_list'),
	url(r'^(?P<id>\d+)/$',		'addon_edit'),
)
