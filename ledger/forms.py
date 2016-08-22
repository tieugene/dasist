# -*- coding: utf-8 -*-
'''
ledger.forms
'''

# 1. django
from django import forms

# 2. system

# 3. 3rd

# 4. my
from bills.models import Payer
from core.models import Org

class	FilterLedgerListForm(forms.Form):
	payer	= forms.ModelChoiceField(queryset=Payer.objects.all().order_by('name'), label=u'Плательщик', required=False)
	shipper	= forms.ModelChoiceField(queryset=Org.objects.all().order_by('name'), label=u'Поставщик', required=False)