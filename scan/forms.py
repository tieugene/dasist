# -*- coding: utf-8 -*-
'''
scan.forms
'''

# 1. django
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

# 2. system
import datetime

# 3. 3rd
from dal import autocomplete

# 4. my
from models import Scan
from bills.models import Place, Subject
from core.models import Org
from core.forms import InnField, chk_new_org, chk_org_names

EMPTY_VALUE = [('', '---'),]

class	FilterScanListForm(forms.Form):
	#place		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект', required=False)
	place		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place')), label=u'Объект', required=False)
	#subject	= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('subject').distinct().values_list('subject', 'subject')), label=u'Подобъект', required=False)
	subject		= forms.ChoiceField(choices=EMPTY_VALUE, label=u'Подобъект', required=False)
	depart		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('depart').distinct().exclude(depart=None).values_list('depart', 'depart')), label=u'Направление', required=False)
	payer		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('payer').distinct().exclude(payer=None).values_list('payer', 'payer')), label=u'Плательщик', required=False)
	#shipper	= forms.ModelChoiceField(queryset=Org.objects.all(), label=u'Поставщик', required=False)
	shipper		= forms.ModelChoiceField(queryset=Org.objects.all(), required=False, widget=autocomplete.ModelSelect2(url='org-autocomplete'))
	billno		= forms.CharField(max_length=64, label=u'Номер счета', required=False)
	#billdate	= forms.DateField(label=u'Дата счета', required=False, widget=forms.TextInput(attrs={'size':8}))
	billdate	= forms.CharField(label=u'Дата счета', required=False, widget=forms.TextInput(attrs={'size':8}))

	def	clean_billdate(self):
		data = self.cleaned_data['billdate']
		#print 'Date:', data
		if data:
			try:
				datetime.datetime.strptime(data, '%d.%m.%y')
				return data
			except ValueError:
				self.cleaned_data['billdate'] = ''
				raise forms.ValidationError('Must be "DD.MM.YY"')

	def __init__(self, *args, **kwargs):
		forms.Form.__init__(self, *args, **kwargs)
		places=EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place'))
		if len(places)==1:
			self.fields['place'].initial=places[0][0]
		place=self.fields['place'].initial or self.initial.get('place') or self._raw_value('place')
		if place:
			# parent is known. Now I can display the matching children.
			subjects=EMPTY_VALUE + list(Scan.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
			self.fields['subject'].choices=subjects
			if len(subjects)==1:
				self.fields['subject'].initial=subjects[0][0]

class	ReplaceDepartForm(forms.Form):
	src		= forms.ChoiceField(choices=Scan.objects.order_by('depart').distinct().values_list('depart', 'depart'), label=u'Направление 1')
	dst		= forms.ChoiceField(choices=Scan.objects.order_by('depart').distinct().values_list('depart', 'depart'), label=u'Направление 2')

class	ReplacePlaceForm(forms.Form):
	src		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект 1')
	place		= forms.ModelChoiceField(queryset=Place.objects.all().order_by('name'), empty_label=None, label=u'Объект')
	subject		= forms.ModelChoiceField(queryset=Subject.objects.all().order_by('name'), label=u'Подобъект', required=False)

class	ScanEditForm(forms.Form):
	'''
	TODO: check inn, supplier uniq
	'''
	place		= forms.ChoiceField(choices = list(Scan.objects.order_by('place').distinct().values_list('place', 'place')), label=u'Объект', required=True)
	subject		= forms.ChoiceField(choices=EMPTY_VALUE, label=u'Подобъект', required=False)
	depart		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('depart').distinct().exclude(depart=None).values_list('depart', 'depart')), label=u'Направление', required=False)
	payer		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('payer').distinct().exclude(payer=None).values_list('payer', 'payer')), label=u'Плательщик', required=True)
	suppinn		= InnField(min_length=10, max_length=12, label=u'ИНН Поставщика', required=True)
	suppname	= forms.CharField(max_length=64, label=u'Поставщик (кратко)', required=True)
	suppfull	= forms.CharField(max_length=64, label=u'Поставщик (полностью)', required=True)
	no		= forms.CharField(max_length=16, label=u'Счет.№', required=True)
	date		= forms.DateField(label=u'Счет.Дата', required=True)
	sum		= forms.DecimalField(max_digits=11, decimal_places=2, label=u'Счет.Сумма', required=True)

	def __init__(self, *args, **kwargs):
		forms.Form.__init__(self, *args, **kwargs)
		places=EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place'))
		if len(places)==1:
			self.fields['place'].initial=places[0][0]
		place=self.fields['place'].initial or self.initial.get('place') or self._raw_value('place')
		if place:
			# parent is known. Now I can display the matching children.
			subjects=EMPTY_VALUE + list(Scan.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
			self.fields['subject'].choices=subjects
			if len(subjects)==1:
				self.fields['subject'].initial=subjects[0][0]

	def clean(self):
		cleaned_data = super(ScanEditForm, self).clean()
		# 1. chk inn<>suppname
		if ('suppinn' in cleaned_data) and ('suppname' in cleaned_data):
			chk_new_org(cleaned_data['suppinn'], cleaned_data['suppname'])
		# 2. chk supp names
		chk_org_names(cleaned_data['suppname'], cleaned_data['suppfull'])
		# X. that's all, folks
		return cleaned_data
