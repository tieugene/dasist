# -*- coding: utf-8 -*-
'''
contrarch.forms
'''

# 1. system
import datetime
# import pprint

# 2. my
from core.models import Org

# 3. 3rd
from dal import autocomplete

# 4. django
from django import forms

from models import Contrarch


EMPTY_VALUE = [('', '---'), ]


class FilterContrarchListForm(forms.Form):
    place = forms.ChoiceField(choices=EMPTY_VALUE + list(Contrarch.objects.order_by('place').distinct().values_list('place', 'place')), label=u'Объект', required=False)
    subject = forms.ChoiceField(choices=EMPTY_VALUE + list(Contrarch.objects.order_by('subject').distinct().values_list('subject', 'subject')), label=u'Подобъект', required=False)
    customer = forms.ChoiceField(choices=EMPTY_VALUE + list(Contrarch.objects.order_by('customer').distinct().exclude(customer=None).values_list('customer', 'customer')), label=u'Заказчик', required=False)
    depart = forms.ChoiceField(choices=EMPTY_VALUE + list(Contrarch.objects.order_by('depart').distinct().exclude(depart=None).values_list('depart', 'depart')), label=u'Направление', required=False)
    payer = forms.ChoiceField(choices=EMPTY_VALUE + list(Contrarch.objects.order_by('payer').distinct().exclude(payer=None).values_list('payer', 'payer')), label=u'Плательщик', required=False)
    shipper = forms.ModelChoiceField(queryset=Org.objects.all(), required=False, widget=autocomplete.ModelSelect2(url='org-autocomplete'))
    docno = forms.CharField(max_length=64, label=u'Номер договора', required=False)
    docdate = forms.CharField(label=u'Дата договора', required=False, widget=forms.TextInput(attrs={'size': 8}))

    def clean_docdate(self):
        data = self.cleaned_data['docdate']
        if data:
            try:
                datetime.datetime.strptime(data, '%d.%m.%y')
                return data
            except ValueError:
                self.cleaned_data['docdate'] = ''
                raise forms.ValidationError('Must be "DD.MM.YY"')

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        places = EMPTY_VALUE + list(Contrarch.objects.order_by('place').distinct().values_list('place', 'place'))
        if len(places) == 1:
            self.fields['place'].initial = places[0][0]
        place = self.fields['place'].initial or self.initial.get('place')
        if place:
            # parent is known. Now I can display the matching children.
            subjects = EMPTY_VALUE + list(Contrarch.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
            self.fields['subject'].choices = subjects
            if len(subjects) == 1:
                self.fields['subject'].initial = subjects[0][0]
