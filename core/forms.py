# -*- coding: utf-8 -*-
'''
'''

from django import forms

import models

class	FileSeqItemAddForm(forms.Form):
	file		= forms.FileField(label=u'Файл', required=False)
