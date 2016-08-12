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
from django.db.models import Q
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
from bills.models import Payer, Bill
from scan.models import Scan

reload(sys)
sys.setdefaultencoding('utf-8')

class	LedgerList(ListView):
	template_name = 'ledger/list.html'
	paginate_by = 25
	filter = {
		'payer':	None,
	}

	def	get_queryset(self):
		# 1. handle session
		self.paginate_by = self.request.session.get('ledger_lpp', 25)
		self.filter['payer'] = self.request.session.get('ledger_payer', None)
		# 2. create query
		if self.filter['payer']:
			payer = Payer.objects.get(pk=self.filter['payer'])
			q = FileSeq.objects.filter(Q(bill__payer=payer) | Q(scan__payer=payer.name))
		else:
			q = FileSeq.objects.all()
		q = q.order_by('-pk')[:100]
		#print q.query
		return q

	def	get_context_data(self, **kwargs):
		context = super(LedgerList, self).get_context_data(**kwargs)
		context['ledger_lpp']	= self.paginate_by
		context['form']	= forms.FilterLedgerListForm(initial={
			'payer': self.filter['payer'],
		})
		return context

@login_required
def	ledger_set_lpp(request, lpp):
	request.session['ledger_lpp'] = int(lpp)
	return redirect('ledger_list')

@login_required
def	ledger_set_filter(request):
	form = forms.FilterLedgerListForm(request.POST)
	if form.is_valid():
		filter = form.cleaned_data
		request.session['ledger_payer'] = filter['payer'].pk if filter['payer'] else None
	return redirect('ledger_list')
