# -*- coding: utf-8 -*-
'''
dasist.core.urls
'''

#from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
	url(r'^f/$',			'file_list'),
	url(r'^f/(?P<id>\d+)/r/$',	'file_view'),
	url(r'^f/(?P<id>\d+)/g/$',	'file_get'),
	url(r'^f/(?P<id>\d+)/d/$',	'file_del'),
	url(r'^f/(?P<id>\d+)/v/$',	'file_preview'),
	url(r'^fs/$',			'fileseq_list'),
	url(r'^fs/(?P<id>\d+)/r/$',	'fileseq_view'),
	url(r'^fs/(?P<id>\d+)/d/$',	'fileseq_del'),
	#url(r'^fs/(?P<id>\d+)/af/$',	'fileseq_add_file'),
	url(r'^fsi/(?P<id>\d+)/d/$',	'fileseqitem_del'),
	url(r'^fsi/(?P<id>\d+)/up/$',	'fileseqitem_move_up'),
	url(r'^fsi/(?P<id>\d+)/down/$',	'fileseqitem_move_down'),
)
