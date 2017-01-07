# -*- coding: utf-8 -*-
'''
urls
dasist 0.?.?
'''

from django.conf import settings


def common_context(context):
    '''
    our context processor. Add to dict vars to send in ALL templates.
    '''
    return {
        'LOGIN_URL':    settings.LOGIN_URL,
        'path':         'apps.core'
    }
