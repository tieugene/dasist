# -*- coding: utf-8 -*-
'''
core.forms
'''

from django import forms

import models

class	FileSeqItemAddForm(forms.Form):
	file		= forms.FileField(label=u'Файл', required=False)

class	InnField(forms.CharField):
	def     __chk_cs(self, s, k):
		'''
		Calculates control summ
		@s:string - inn
		@k:tupple - digits positions to calculate
		'''
		sum = 0
		l = len(k)
		for i in xrange(l):
			sum += int(s[i]) * k[i]
		#print ((sum%11)%10)%11
		return ((sum%11)%10)%11 == int(s[l])	# ?..
	def     validate(self, value):
		super(InnField, self).validate(value)
		if (not value.isdigit()):
			raise forms.ValidationError('Должны быть только цифры')
		if (len(value) not in set([10, 12])):
			raise forms.ValidationError('Должно быть 10 или 12 цифр')
		if (len(value) == 10):
			if not self.__chk_cs(value, (2, 4, 10, 3, 5, 9, 4, 6, 8)):
				raise forms.ValidationError('Контрольная сумма цифр неверна')
		else:
			if not (self.__chk_cs(value, (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)) and self.__chk_cs(value, (7, 2, 4, 10, 3, 5, 9, 4, 6, 8))):
				raise forms.ValidationError('Контрольные суммы цифр неверны')

def	chk_new_org(inn, name):
	'''
	Check new shipper on uniqueness
	@f:form object
	@flds:tupple - field to check (inn, shorname)
	'''
	orgs = models.Org.objects.filter(name=name.strip())
	if (orgs.count()) and (orgs[0].inn != inn.strip()):
		raise forms.ValidationError('Поставщик с таким кратким наименованием и другим ИНН уже есть')

def	chk_org_names(shortname, fullname):
	if (shortname.strip() == fullname.strip()):
		raise forms.ValidationError('Краткое и Полное наименования Поставщика совпадают. Не надо так делать.')

class	OrgEditForm(forms.ModelForm):
	class Meta:
		model = models.Org
		exclude = []
