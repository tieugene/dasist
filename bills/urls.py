# -*- coding: utf-8 -*-
'''
bills.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = (
    # 'bills.views',
    url(r'^$',                      login_required(views.BillList.as_view()), name='bill_list'),
    url(r'^lpp/(?P<lpp>\d+)/$',     views.bill_set_lpp, name='bill_set_lpp'),
    url(r'^mode/(?P<mode>\d+)/$',   views.bill_set_mode, name='bill_set_mode'),
    url(r'^fs/$',                   views.bill_filter_state, name='bill_filter_state'),
    url(r'^get_subjs/$',            views.bill_get_subjects, name='bill_get_subjects'),
    url(r'^a/$',                    views.bill_add, name='bill_add'),           # GET/POST; ACL: assign, Cancel > list; save > view (Draft)
    url(r'^(?P<id>\d+)/$',          views.bill_view, name='bill_view'),         # GET; ACL: assign|approv
    url(r'^(?P<id>\d+)/u/$',        views.bill_edit, name='bill_edit'),         # GET/POST; ACL: assign+draft;
    url(r'^(?P<id>\d+)/ru/$',       views.bill_reedit, name='bill_reedit'),     # GET/POST; ACL: assign+draft?;
    url(r'^(?P<id>\d+)/d/$',        views.bill_delete, name='bill_delete'),     # GET; ACL: assign;
    url(r'^(?P<id>\d+)/s/$',        views.bill_toscan, name='bill_toscan'),
    url(r'^(?P<id>\d+)/r/$',        views.bill_restart, name='bill_restart'),
    url(r'^(?P<id>\d+)/id/$',       views.bill_img_del, name='bill_img_del'),
    url(r'^(?P<id>\d+)/iup/$',      views.bill_img_up, name='bill_img_up'),
    url(r'^(?P<id>\d+)/idn/$',      views.bill_img_dn, name='bill_img_dn'),
    url(r'^(?P<id>\d+)/irl/$',      views.bill_img_rl, name='bill_img_rl'),
    url(r'^(?P<id>\d+)/irr/$',      views.bill_img_rr, name='bill_img_rr'),
    url(r'^(?P<id>\d+)/mail/$',     views.bill_mail, name='bill_mail'),
    # url(r'^(?P<id>\d+)/g/$',       'bill_get'),  # GET; ACL: assign;
)
