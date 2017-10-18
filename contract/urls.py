# -*- coding: utf-8 -*-
'''
contract.urls
'''

from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = (
    url(r'^$',                      login_required(views.ContractList.as_view()), name='contract_list'),
    url(r'^lpp/(?P<lpp>\d+)/$',     views.contract_set_lpp, name='contract_set_lpp'),
    url(r'^mode/(?P<mode>\d+)/$',   views.contract_set_mode, name='contract_set_mode'),
    url(r'^fs/$',                   views.contract_filter_state, name='contract_filter_state'),
    url(r'^get_subjs/$',            views.contract_get_subjects, name='contract_get_subjects'),
    url(r'^a/$',                    views.contract_add, name='contract_add'),           # GET/POST; ACL: assign, Cancel > list; save > view (Draft)
    url(r'^(?P<id>\d+)/$',          views.contract_view, name='contract_view'),         # GET; ACL: assign|approv
    url(r'^(?P<id>\d+)/u/$',        views.contract_edit, name='contract_edit'),         # GET/POST; ACL: assign+draft;
    url(r'^(?P<id>\d+)/d/$',        views.contract_delete, name='contract_delete'),     # GET; ACL: assign;
    url(r'^(?P<id>\d+)/r/$',        views.contract_restart, name='contract_restart'),
    url(r'^(?P<id>\d+)/id/$',       views.contract_img_del, name='contract_img_del'),
    url(r'^(?P<id>\d+)/iup/$',      views.contract_img_up, name='contract_img_up'),
    url(r'^(?P<id>\d+)/idn/$',      views.contract_img_dn, name='contract_img_dn'),
    url(r'^(?P<id>\d+)/mail/$',     views.contract_mail, name='contract_mail'),
    url(r'^(?P<id>\d+)/a/$',        views.contract_toarch, name='contract_toarch'),
    # url(r'^(?P<id>\d+)/g/$',       'contract_get'),  # GET; ACL: assign;
)
