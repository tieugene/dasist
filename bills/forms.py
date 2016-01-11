# -*- coding: utf-8 -*-
'''
bills.forms
'''

from django import forms
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.db.models.fields.files import FieldFile

#import models
from bills.models import Approver, Place, Subject, Department, Payer, Bill
from core.models import Org
from core.forms import InnField, chk_new_org, chk_org_names

import decimal, pprint

mime_available = set((
	'image/png',
	'image/tiff',
	'image/jpeg',
	'application/pdf',
))

class	ApproverModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.get_fio()

class	ResumeForm(forms.Form):
	note	= forms.CharField(max_length=255, label='Комментарий', required = False, widget=forms.TextInput(attrs={'size':80}))

class	FilterBillListForm(forms.Form):
	draft	= forms.BooleanField(label='Черновики',	required = False)
	onway	= forms.BooleanField(label='В пути',	required = False)
	onpay	= forms.BooleanField(label='В оплате',	required = False)
	done	= forms.BooleanField(label='Исполнены',	required = False)
	dead	= forms.BooleanField(label='Завернуты',	required = False)
	place	= forms.ModelChoiceField(queryset=Place.objects.all().order_by('name'), label=u'Объект', required=False)
	subject	= forms.ModelChoiceField(queryset=Subject.objects.none().order_by('name'), label=u'Подобъект', required=False)
	#subject = forms.ChoiceField(choices=EMPTY_VALUE, label=u'Подобъект', required=False)
	depart	= forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'), label=u'Направление', required=False)
	shipper	= forms.ModelChoiceField(queryset=Org.objects.all().order_by('name'), label=u'Поставщик', required=False)
	payer	= forms.ModelChoiceField(queryset=Payer.objects.all().order_by('name'), label=u'Поставщик', required=False)

	def __init__(self, *args, **kwargs):
		forms.Form.__init__(self, *args, **kwargs)
		# None or unicode/int
		place = self.fields['place'].initial or self.initial.get('place') or self._raw_value('place')
		if place:
			# parent is known. Now I can display the matching children.
			self.fields['subject'].queryset = Subject.objects.filter(place__pk=int(place)).order_by('name')

class	BillAddFileForm(forms.Form):
	file		= forms.FileField(label=u'Файл')
	rawpdf		= forms.BooleanField(label=u'Конвертировать PDF', required=False)

	def clean_file(self):
		file = self.cleaned_data['file']
		if (not isinstance(file, FieldFile)) and (file.content_type not in mime_available):
			raise forms.ValidationError('File must be PNG, TIF, JPG or PDF!')
		return None

class	BillForm(forms.Form):
	'''
	Parent form; abstract only.
	'''
	file		= forms.FileField(label=u'Скан')
	rawpdf		= forms.BooleanField(label=u'Конвертировать PDF', required=False)
	place		= forms.ModelChoiceField(queryset=Place.objects.all().order_by('name'), empty_label=None, label=u'Объект')
	subject		= forms.ModelChoiceField(queryset=Subject.objects.all().order_by('name'), label=u'Подобъект', required=False)
	depart		= forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'), label=u'Направление', required=False)
	payer		= forms.ModelChoiceField(queryset=Payer.objects.all().order_by('name'), empty_label='---', label=u'Плательщик')
	suppinn		= InnField(min_length=10, max_length=12, label=u'ИНН Поставщика', required=True)
	suppname	= forms.CharField(max_length=64, label=u'Поставщик (кратко)', required=True)
	suppfull	= forms.CharField(max_length=64, label=u'Поставщик (полностью)', required=True)
	billno		= forms.CharField(max_length=64, label=u'Номер счета')
	billdate	= forms.DateField(label=u'Дата счета')
	billsum		= forms.DecimalField(max_digits=11, decimal_places=2, min_value=decimal.Decimal('0.01'), localize=True, label=u'Сумма счета')
	payedsum	= forms.DecimalField(max_digits=11, decimal_places=2, min_value=decimal.Decimal('0.00'), localize=True, label=u'Оплачено')
	topaysum	= forms.DecimalField(max_digits=11, decimal_places=2, min_value=decimal.Decimal('0.00'), localize=True, label=u'Сумма к оплате')
	mgr		= ApproverModelChoiceField(queryset=Approver.objects.filter(role__pk=3), empty_label=None, label=u'Руководитель', widget=forms.RadioSelect)
	boss		= ApproverModelChoiceField(queryset=Approver.objects.filter(role__pk=5), empty_label=None, label=u'Гендиректор', widget=forms.RadioSelect)

	def clean(self):
		cleaned_data = super(BillForm, self).clean()
		# 1. chk inn<>suppname
		suppinn = cleaned_data.get('suppinn')
		suppname = cleaned_data.get('suppname')
		suppfull = cleaned_data.get('suppfull')
		if (suppinn and suppname):
			chk_new_org(suppinn, suppname)
		# 2. chk supp names
		if (suppname and suppfull):
			chk_org_names(suppname, suppfull)
		# 3. chk summs
		billsum = cleaned_data.get('billsum')
		payedsum = cleaned_data.get('payedsum')
		topaysum = cleaned_data.get('topaysum')
		if (billsum == None):
			raise forms.ValidationError('Заполните сумму счета.')
		if (payedsum == None):
			raise forms.ValidationError('Заполните Оплачено.')
		if (topaysum == None):
			raise forms.ValidationError('Заполните сумму к оплате.')
		if (payedsum > billsum):
			raise forms.ValidationError('Оплачено больше суммы счета.')
		if (topaysum > (billsum - payedsum)):
			raise forms.ValidationError('К оплате больше чем надо.')
		# X. that's all, folks
		return cleaned_data

class	BillAddForm(BillForm):
	'''
	Add new bill
	'''
	def clean_file(self):
		file = self.cleaned_data['file']
		if (not isinstance(file, FieldFile)) and (file.content_type not in mime_available):
			raise forms.ValidationError('File must be PNG, TIF, JPG or PDF!')
		return None

	def clean(self):
		cleaned_data = super(BillAddForm, self).clean()
		# 4. chk unqueness
		shipper__inn = cleaned_data.get('suppinn')
		billno = cleaned_data.get('billno')
		billdate = cleaned_data.get('billdate')
		if (shipper__inn and billno and billdate):
			if Bill.objects.filter(
				shipper__inn = shipper__inn,
				billno = billno,
				billdate = billdate
			).exists():
				raise forms.ValidationError('Такой счет уже есть.')
		return cleaned_data

class	BillEditForm(BillForm):
	'''
	Edit existance bill (not locked)
	'''
	id		= forms.IntegerField(label=u'ID', widget=forms.HiddenInput())
	file		= forms.FileField(label=u'Скан', required=False, help_text=u'(Выберите файл, если хотите заменить скан)')

	def clean_file(self):
		file = self.cleaned_data['file']
		if (file):
			if (not isinstance(file, FieldFile)) and (file.content_type not in mime_available):
				raise forms.ValidationError('File must be PNG, TIF, JPG or PDF!')
		return None

	def clean(self):
		cleaned_data = super(BillEditForm, self).clean()
		# 4. chk unqueness
		if Bill.objects.filter(
			shipper__inn = cleaned_data['suppinn'],
			billno = cleaned_data['billno'],
			billdate = cleaned_data['billdate']
		).exclude(fileseq_id = int(cleaned_data['id'])).exists():
			raise forms.ValidationError('Такой счет уже есть.')
		return cleaned_data

class	BillReEditForm(forms.Form):
	'''
	Edit locked bill
	'''
	topaysum	= forms.DecimalField(max_digits=11, decimal_places=2, min_value=decimal.Decimal('0.01'), localize=True, label=u'Сумма к оплате')
	mgr		= ApproverModelChoiceField(queryset=Approver.objects.filter(role__pk=3), empty_label=None, label=u'Руководитель', widget=forms.RadioSelect)
	boss		= ApproverModelChoiceField(queryset=Approver.objects.filter(role__pk=5), empty_label=None, label=u'Гендиректор', widget=forms.RadioSelect)

	def	__init__(self, *args, **kwargs):
		if ('max_topaysum') in kwargs:
			self.max_topaysum = kwargs.pop('max_topaysum')
		else:
			self.max_topaysum = None
		super(BillReEditForm, self).__init__(*args, **kwargs)

	def clean_topaysum(self):
		topaysum = self.cleaned_data['topaysum']
		if (self.max_topaysum):
			if  topaysum> self.max_topaysum:
				raise forms.ValidationError('Больше %s не дадут' % self.max_topaysum)
				return None
		return topaysum
