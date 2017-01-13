# -*- coding: utf-8 -*-
'''
urls
'''
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView
from django.views.i18n import javascript_catalog

admin.autodiscover()

urlpatterns = [
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^admin/jsi18n',       javascript_catalog),    # hack to use admin form widgets
    url(r'^accounts/login/$',   login),
    url(r'^logout$',            logout),
    url(r'^$',                  TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^about$',             TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^core/',              include('core.urls')),
    url(r'^bills/',             include('bills.urls')),
    url(r'^scan/',              include('scan.urls')),
    url(r'^ledger/',            include('ledger.urls')),
    # url(r'^contract/',          include('contract.urls')),
]
urlpatterns += staticfiles_urlpatterns()
