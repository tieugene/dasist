# -*- coding: utf-8 -*-
'''
dasist.core.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = (
    # 'core.views',
    url(r'^f/$',                    login_required(views.FileList.as_view()), name='file_list'),
    url(r'^f/(?P<pk>\d+)/r/$',      login_required(views.FileDetail.as_view()), name='file_view'),
    url(r'^f/(?P<id>\d+)/g/$',      views.file_get, name='file_get'),
    url(r'^f/(?P<id>\d+)/d/$',      views.file_del, name='file_del'),
    url(r'^f/(?P<id>\d+)/v/$',      views.file_preview, name='file_preview'),
    url(r'^fs/$',                   login_required(views.FileSeqList.as_view()), name='fileseq_list'),
    url(r'^fs/(?P<pk>\d+)/r/$',     login_required(views.FileSeqDetail.as_view()), name='fileseq_view'),
    url(r'^fs/(?P<id>\d+)/d/$',     views.fileseq_del, name='fileseq_del'),
    url(r'^fs/(?P<id>\d+)/af/$',    views.fileseq_add_file, name='fileseq_add_file'),
    url(r'^fsi/(?P<id>\d+)/d/$',    views.fileseqitem_del, name='fileseqitem_del'),
    url(r'^fsi/(?P<id>\d+)/up/$',   views.fileseqitem_move_up, name='fileseqitem_move_up'),
    url(r'^fsi/(?P<id>\d+)/down/$', views.fileseqitem_move_down, name='fileseqitem_move_down'),
    url(r'^o/$',                    login_required(views.OrgList.as_view()), name='org_list'),
    url(r'^o/(?P<pk>\d+)/r/$',      login_required(views.OrgDetail.as_view()), name='org_view'),
    url(r'^o/(?P<id>\d+)/u/$',      views.org_edit, name='org_edit'),
    url(r'^o/get_by_inn/$',         views.org_get_by_inn, name='org_get_by_inn'),
    url('org-autocomplete/$',       views.OrgAutocomplete.as_view(), name='org-autocomplete',),

)
