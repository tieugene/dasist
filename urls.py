from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$',		'views.index'),
	url(r'^admin/',		include(admin.site.urls)),
	url(r'^admin/jsi18n',	'django.views.i18n.javascript_catalog'), # hack to use admin form widgets
	#(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
	url(r'^accounts/login/$',		login),
	url(r'^logout$',	logout),
	url(r'^core/',		include('core.urls')),
	url(r'^bills/',		include('bills.urls')),
	url(r'^scan/',		include('scan.urls')),
	url(r'^about$',		'views.about'),
	#(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

#urlpatterns += staticfiles_urlpatterns()
