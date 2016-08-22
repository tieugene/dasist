# -*- coding: utf-8 -*-
'''
ledger.views
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import ListView

# 2. system
import sys

# 3. 3rd party

# 4. my
import forms
from core.models import FileSeq, Org
from bills.models import Payer, Approver
from bills.views_extras import ROLE_ASSIGNEE, ROLE_BOSS, ROLE_ACCOUNTER

reload(sys)
sys.setdefaultencoding('utf-8')

class	LedgerList(ListView):
	'''
	TODO: Гендир, Бухгалтер, Исполнитель
	'''
	template_name = 'ledger/list.html'
	paginate_by = 25
	filter = {
		'payer':	None,
		'shipper':	None,
	}
	enabled_users = set([ROLE_ASSIGNEE, ROLE_BOSS, ROLE_ACCOUNTER])

	def	get_queryset(self):
		user = self.request.user
		self.approver = Approver.objects.get(user=user)
		role_id = self.approver.role.pk
		# 1. handle session
		self.paginate_by = self.request.session.get('ledger_lpp', 25)
		self.filter['payer'] = self.request.session.get('ledger_payer', None)
		self.filter['shipper'] = self.request.session.get('ledger_shipper', None)
		q = FileSeq.objects
		# 2. create query
		if (role_id in self.enabled_users) or user.is_superuser:
			payer	= Payer.objects.get(pk=self.filter['payer']) if self.filter['payer'] else None
			shipper	= Org.objects.get(pk=self.filter['shipper']) if self.filter['shipper'] else None
			if payer or shipper:
				if payer:
					q = q.filter(Q(bill__payer=payer) | Q(scan__payer=payer.name))
				if shipper:
					q = q.filter(Q(bill__shipper=shipper) | Q(scan__shipper=shipper))
			else:
				q = q.all()
			q = q.order_by('-pk')	#[:100]
		else:
			q = q.none()
		#print q.query
		return q

	def	get_context_data(self, **kwargs):
		context = super(LedgerList, self).get_context_data(**kwargs)
		context['ledger_lpp']	= self.paginate_by
		context['form']	= forms.FilterLedgerListForm(initial={
			'payer': self.filter['payer'],
			'shipper': self.filter['shipper'],
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
		request.session['ledger_shipper'] = filter['shipper'].pk if filter['shipper'] else None
	return redirect('ledger_list')
