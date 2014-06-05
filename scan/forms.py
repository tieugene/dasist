# -*- coding: utf-8 -*-

from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

from models import Scan
from bills.models import Place, Subject

EMPTY_VALUE = [('', '---'),]

class	FilterScanListForm(forms.Form):
	#place		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект', required=False)
	place		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place')), label=u'Объект', required=False)
#	#subject
	depart		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('depart').distinct().values_list('depart', 'depart')), label=u'Направление', required=False)
	supplier	= forms.CharField(max_length=64, label=u'Поставщик', required=False)
	billno		= forms.CharField(max_length=64, label=u'Номер счета', required=False)
	billdate	= forms.DateField(label=u'Дата счета', required=False, widget=forms.TextInput(attrs={'size':8}))

class	ReplaceDepartForm(forms.Form):
	src		= forms.ChoiceField(choices=Scan.objects.order_by('depart').distinct().values_list('depart', 'depart'), label=u'Направление 1')
	dst		= forms.ChoiceField(choices=Scan.objects.order_by('depart').distinct().values_list('depart', 'depart'), label=u'Направление 2')

#class	ReplacePlaceForm(forms.Form):
#	src		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект 1')
#	dst		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект 2')
#	subj		= forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('subject').distinct().values_list('subject', 'subject')), label=u'ПодОбъект', required=False)

class	ReplacePlaceForm(forms.Form):
	src		= forms.ChoiceField(choices=Scan.objects.order_by('place').distinct().values_list('place', 'place'), label=u'Объект 1')
	place		= forms.ModelChoiceField(queryset=Place.objects.all().order_by('name'), empty_label=None, label=u'Объект')
	subject		= forms.ModelChoiceField(queryset=Subject.objects.all().order_by('name'), label=u'Подобъект', required=False)
