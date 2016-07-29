# -*- coding: utf-8 -*-
'''
ledger.forms
'''

# 1. django
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

# 2. system

# 3. 3rd

# 4. my
from bills.models import Payer

class	FilterLedgerListForm(forms.Form):
	payer	= forms.ModelChoiceField(queryset=Payer.objects.all().order_by('name'), label=u'Поставщик', required=False)
