SECRET_KEY = '-^i&r%be$bz_6yd=#-t2ni@_dl4vs(e+n^lihh#(3_rhg*#x1^'
#DEBUG = True
#DEBUG = False

#STATIC_URL = '/static_dasist/'

#DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/mnt/shares/tmp/dasist_real.db'}}
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': 'unix:/tmp/memcached.sock',
#    }
#}
# Email
'''
EMAIL_HOST = 'smtp.timeweb.ru'
EMAIL_PORT = '465'
EMAIL_SUBJECT_PREFIX = '[DasIst] '
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'ti.eugene@garantstroyspb.ru'
EMAIL_HOST_PASSWORD = 'trititi'
'''
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '465'
EMAIL_SUBJECT_PREFIX = '[DasIst] '
EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'ti.eugene.support'
EMAIL_HOST_PASSWORD = 'UktelMuctel'
# alt: cat ~/initial-setup-ks.cfg | mail -s test6_via_gmail ti.eugene@gmail.com