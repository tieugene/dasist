# -*- coding: utf-8 -*-
'''
ledger.forms
'''

# 1. my
from bills.models import Payer

from core.models import Org
from scan.models import Scan

# 2. django
from django import forms

EMPTY_VALUE = [('', '---'), ]

class FilterLedgerListForm(forms.Form):
    payer = forms.ModelChoiceField(
        queryset=Payer.objects.all().order_by('name'),
        label=u'Плательщик',
        required=False)
    shipper = forms.ModelChoiceField(
        queryset=Org.objects.all().order_by('name'),
        label=u'Поставщик',
        required=False)


class FilterSummaryListForm(forms.Form):
    place = forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place')), label=u'Объект', required=False)
    subject = forms.ChoiceField(choices=EMPTY_VALUE + list(Scan.objects.order_by('subject').distinct().values_list('subject', 'subject')), label=u'Подобъект', required=False)
    year = forms.ChoiceField(choices=EMPTY_VALUE + [('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017')], label=u'Год', required=False)
