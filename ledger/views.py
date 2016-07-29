# -*- coding: utf-8 -*-
'''
ledger.views
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic import ListView, DetailView
from django.utils.datastructures import SortedDict
from django.db.models import F
from django.core.files.storage import default_storage	# MEDIA_ROOT
from django.utils.decorators import method_decorator

# 2. system
import os, sys, pprint

# 3. 3rd party
# 4. my
import forms
from core.models import FileSeq

reload(sys)
sys.setdefaultencoding('utf-8')

class	LedgerList(ListView):
	template_name = 'ledger/list.html'
	paginate_by = 25
	filter = {
		'payer':	None,
	}

	def	get_queryset(self):
		#print 'LedgerList get_queryset'
		# 1. handle session
		self.paginate_by = self.request.session.get('ledger_lpp', 25)
		self.filter['payer'] =		self.request.session.get('ledger_payer', None)
		# 2. create query
		q = FileSeq.objects.all().order_by('-pk')[:100]
		if self.filter['payer']:
			pass
		#	q = q.filter(payer__contains=self.filter['payer'])
		return q

	def	get_context_data(self, **kwargs):
		#print 'LedgerList get_context_data'
		context = super(LedgerList, self).get_context_data(**kwargs)
		context['ledger_lpp']	= self.paginate_by
		context['form']	= forms.FilterLedgerListForm(initial={
			'payer':	self.filter['payer'],
		})
		return context

@login_required
def	ledger_set_lpp(request, lpp):
	request.session['ledger_lpp'] = int(lpp)
	return redirect('ledger_list')

@login_required
def	ledger_set_filter(request):
	form = forms.FilterScanListForm(request.POST)
	if form.is_valid():
		filter = form.cleaned_data
		#print "Set filter:", filter['billdate']
		request.session['ledger_payer'] =		filter['payer']
	return redirect('ledger_list')
