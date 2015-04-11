# -*- coding: utf-8 -*-
SECRET_KEY = '-^i&r%be$bz_6yd=#-t2ni@_dl4vs(e+n^lihh#(3_rhg*#x1^'
DEBUG = True
#DEBUG = False

STATIC_URL = '/static_dasist/'
ADMIN_MEDIA_PREFIX = '/static_dasist/admin/'

MEDIA_ROOT = '/mnt/shares/tmp/dasist-0.1.3/media/'
DATABASES = {'default': {
	#'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/mnt/shares/tmp/dasist-0.1.3/dasist.db'
	'ENGINE': 'django.db.backends.mysql', 'NAME': 'dasist', 'USER': 'dasist', 'PASSWORD': 'dasist', 'HOST': 'localhost'
}}
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': 'unix:/tmp/memcached.sock',
#    }
#}
# Email
'''
# TimeWeb (not works)
EMAIL_HOST = 'smtp.timeweb.ru'
EMAIL_PORT = '465'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'ti.eugene@garantstroyspb.ru'
EMAIL_HOST_PASSWORD = 'trititi'
# GMail (closed)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'dasist.robot@gmail.com'
EMAIL_HOST_PASSWORD = 'UktelMuctel'
EMAIL_FROM = '"Согласование" <dasist.robot@gmail.com>'
'''
# ManDrill
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'dasist.robot@garantstroyspb.ru'
EMAIL_HOST_PASSWORD = 'Cj3guwr9xAVIAc9BR_1CBA'
EMAIL_FROM = '"Согласование" <dasist.robot@garantstroyspb.ru>'

# alt: cat ~/initial-setup-ks.cfg | mail -s test6_via_gmail ti.eugene@gmail.com
EMAIL_SUBJECT_PREFIX = '[DasIst] '
EMAIL_DUP = 'ti.eugene@gmail.com'
