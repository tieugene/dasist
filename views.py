# -*- coding: utf-8 -*-
from django.shortcuts import redirect
#from django.views.generic.simple import direct_to_template
from django.views.generic.base import TemplateView
from django.conf import settings

def	index(request):
	#return redirect('bills.views.bill_list')
	#return direct_to_template(request, 'index.html')
	#return TemplateView.as_view(request, template_name='index.html')

def	about(request):
	#return TemplateView.as_view(template_name='about.html')

def	common_context(context):
	'''
	our context processor. Add to dict vars to send in ALL templates.
	'''
	return {
		'LOGIN_URL' : settings.LOGIN_URL,
		'path': 'apps.core'
	}
