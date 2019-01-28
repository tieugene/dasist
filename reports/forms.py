# -*- coding: utf-8 -*-
'''
ledger.forms
'''

# 1. my
from bills.models import Payer

from core.models import Org

# 2. django
from django import forms

from scan.models import Scan

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
    year = forms.ChoiceField(choices=EMPTY_VALUE + [('2013', '2013'), ('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017'), ('2018', '2018')], label=u'Год', required=False)

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        places = EMPTY_VALUE + list(Scan.objects.order_by('place').distinct().values_list('place', 'place'))
        if len(places) == 1:
            self.fields['place'].initial = places[0][0]
        # place = self.fields['place'].initial or self.initial.get('place') or self._raw_value('place')
        place = self.fields['place'].initial or self.initial.get('place')
        if place:
            # parent is known. Now I can display the matching children.
            subjects = EMPTY_VALUE + list(Scan.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
            self.fields['subject'].choices = subjects
            if len(subjects) == 1:
                self.fields['subject'].initial = subjects[0][0]
