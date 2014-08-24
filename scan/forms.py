# -*- coding: utf-8 -*-

from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

import datetime

from models import Scan
from bills.models import Place, Subject

EMPTY_VALUE = [('', '---'),]

class	FilterScanListForm(forms.Form):
	#place		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект', required=False)
	place		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place')), label=u'Объект', required=False)
	#subject		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('subject').distinct().values_list('subject', 'subject')), label=u'Подобъект', required=False)
	subject		= forms.ChoiceField(choices=EMPTY_VALUE, label=u'Подобъект', required=False)
	depart		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('depart').distinct().exclude(depart=None).values_list('depart', 'depart')), label=u'Направление', required=False)
	supplier	= forms.CharField(max_length=64, label=u'Поставщик', required=False)
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

class	ScanEditForm(forms.ModelForm):
	class Meta:
		model = Scan
		exclude = ['fileseq']
