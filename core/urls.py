# -*- coding: utf-8 -*-
'''
dasist.core.urls
'''

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

import views

urlpatterns = patterns('core.views',
	#url(r'^f/$',			'file_list'),
	#url(r'^f/(?P<pk>\d+)/r/$',	'file_view'),
	url(r'^f/$',			login_required(views.FileList.as_view()), name='file_list'),
	url(r'^f/(?P<pk>\d+)/r/$',	login_required(views.FileDetail.as_view()), name='file_view'),
	url(r'^f/(?P<id>\d+)/g/$',	'file_get'),
	url(r'^f/(?P<id>\d+)/d/$',	'file_del'),
	url(r'^f/(?P<id>\d+)/v/$',	'file_preview'),
	#url(r'^fs/$',			'fileseq_list'),
	#url(r'^fs/(?P<id>\d+)/r/$',	'fileseq_view'),
	url(r'^fs/$',			login_required(views.FileSeqList.as_view()), name='fileseq_list'),
	url(r'^fs/(?P<pk>\d+)/r/$',	login_required(views.FileSeqDetail.as_view()), name='fileseq_view'),
	url(r'^fs/(?P<id>\d+)/d/$',	'fileseq_del'),
	url(r'^fs/(?P<id>\d+)/af/$',	'fileseq_add_file'),
	url(r'^fsi/(?P<id>\d+)/d/$',	'fileseqitem_del'),
	url(r'^fsi/(?P<id>\d+)/up/$',	'fileseqitem_move_up'),
	url(r'^fsi/(?P<id>\d+)/down/$',	'fileseqitem_move_down'),
	url(r'^o/$',			login_required(views.OrgList.as_view()), name='org_list'),
	url(r'^o/(?P<pk>\d+)/r/$',	login_required(views.OrgDetail.as_view()), name='org_view'),
	url(r'^o/(?P<id>\d+)/u/$',	'org_edit'),
	url(r'^o/get_by_inn/$',		'org_get_by_inn'),
)
