# -*- coding: utf-8 -*-
'''
http://snipt.net/danfreak/how-to-generate-a-dynamic-at-runtime-form-in-django/
TODO: widget=TinyMCE(
'''

from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.db.models.fields.files import FieldFile

import pprint

import models

#class	BillAddForm(forms.Form):
#	img = forms.ImageField()
#	project	= forms.CharField(max_length=64, verbose_name=u'Объект')
#	depart	= forms.CharField(max_length=64, verbose_name=u'Направление')

mime_available = set((
	'image/png',
	'image/tiff',
	'application/pdf',
))

class	BillForm(forms.ModelForm):
	#img = forms.FileField()	# name, size, content_type, temporary_file_path,

	class Meta:
		model = models.Bill
		exclude = ('name', 'mime', 'md5', 'size', 'pages', 'assign', 'approve', 'isalive', 'isgood', 'history')

	def clean(self):
		cleaned_data = super(BillForm, self).clean()
		route = cleaned_data.get('route')
		if (len(route) == 0):	# 1. can't be empty
			raise forms.ValidationError('Маршрут не может быть пустым')
		if (route[-1].role.pk != 3):	# 2. must ends with accounter
			raise forms.ValidationError('Маршрут должен заканчиваться бухгалтером')
		img = self.cleaned_data['file']
		if (not isinstance(img, FieldFile)) and (img.content_type not in mime_available):
			raise forms.ValidationError('File must be PNG, TIF or PDF!')
		return cleaned_data

class	ResumeForm(forms.Form):
	note	= forms.CharField(label='Комментарий', required = False, widget=forms.Textarea)

class	FilterStateForm(forms.Form):
	draft	= forms.BooleanField(label='Черновики:',	required = False)
	onway	= forms.BooleanField(label='В пути:',	required = False)
	done	= forms.BooleanField(label='Исполнены:',	required = False)
	dead	= forms.BooleanField(label='Завернуты:',	required = False)
