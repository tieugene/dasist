# -*- coding: utf-8 -*-
'''
'''

from django import forms

from models import AddOn

class	AddOnForm(forms.ModelForm):
	#bill = forms.CharField(widget=forms.HiddenInput())
	class       Meta:
		model = AddOn
		#fields = ('lastname', 'firstname', 'midname', 'birthdate', 'sex')
		widgets = {'bill': forms.HiddenInput()}