#!/usr/bin/env python
'''
Reset some passwords.
Requires: django_extensions.
Call: ./manage.py runscript rpass.py
'''

from django.contrib.auth.models import User
users = ('02', '03', '05', '14', '42', '44', '45')
for i in users:
    u = User.objects.get(username='user%s' % i)
    u.set_password('pass%s' % i)
    u.save()
