#from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
#from django.core.urlresolvers import reverse
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
	#url(r'^$',		'views.index'),
	url(r'^$',		TemplateView.as_view(template_name='index.html'), name='index'),
	url(r'^admin/',		include(admin.site.urls)),
	url(r'^admin/jsi18n',	'django.views.i18n.javascript_catalog'), # hack to use admin form widgets
	#(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
	url(r'^accounts/login/$',		login),
	url(r'^logout$',	logout),
	url(r'^core/',		include('core.urls')),
	url(r'^bills/',		include('bills.urls')),
	url(r'^scan/',		include('scan.urls')),
	#url(r'^about$',		'views.about'),
	url(r'^about$',		TemplateView.as_view(template_name='about.html'), name='about'),
)
urlpatterns += staticfiles_urlpatterns()
