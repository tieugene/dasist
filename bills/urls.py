# -*- coding: utf-8 -*-
'''
bills.urls
'''

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import views

urlpatterns = patterns('bills.views',
	url(r'^$',			login_required(views.BillList.as_view()), name='bill_list'),
	url(r'^lpp/(?P<lpp>\d+)/$',	'bill_set_lpp'),
	url(r'^mode/(?P<mode>\d+)/$',	'bill_set_mode'),
	url(r'^fs/$',			'bill_filter_state'),
	url(r'^a/$',			'bill_add'),		# GET/POST; ACL: assign, Cancel > list; save > view (Draft)
	url(r'^(?P<id>\d+)/$',		'bill_view'),		# GET; ACL: assign|approv
	url(r'^(?P<id>\d+)/u/$',	'bill_edit'),		# GET/POST; ACL: assign+draft;
	url(r'^(?P<id>\d+)/ru/$',	'bill_reedit'),		# GET/POST; ACL: assign+draft?;
	url(r'^(?P<id>\d+)/d/$',	'bill_delete'),		# GET; ACL: assign;
	url(r'^(?P<id>\d+)/s/$',	'bill_toscan'),
	url(r'^(?P<id>\d+)/r/$',	'bill_restart'),
	url(r'^(?P<id>\d+)/id/$',	'bill_img_del'),
	url(r'^(?P<id>\d+)/iup/$',	'bill_img_up'),
	url(r'^(?P<id>\d+)/idn/$',	'bill_img_dn'),
	url(r'^(?P<id>\d+)/irl/$',	'bill_img_rl'),
	url(r'^(?P<id>\d+)/irr/$',	'bill_img_rr'),
	url(r'^(?P<id>\d+)/mail/$',	'bill_mail'),
#	url(r'^(?P<id>\d+)/g/$',	'bill_get'),		# GET; ACL: assign;
)
