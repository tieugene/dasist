# -*- coding: utf-8 -*-
'''
reports.views
'''

# 1. system
import sys

from bills.models import Approver, Payer, Place
from bills.views_extras import ROLE_ACCOUNTER, ROLE_ASSIGNEE, ROLE_BOSS

from core.models import FileSeq, Org

# 2. django
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.generic import ListView

# 3. my
from scan.models import Scan

from . import forms

reload(sys)
sys.setdefaultencoding('utf-8')


class LedgerList(ListView):
    '''
    TODO: Гендир, Бухгалтер, Исполнитель
    '''
    template_name = 'reports/ledger_list.html'
    paginate_by = 25
    filter = {
        'payer':    None,
        'shipper':  None,
    }
    enabled_users = set([ROLE_ASSIGNEE, ROLE_BOSS, ROLE_ACCOUNTER])

    def get_queryset(self):
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
            payer = Payer.objects.get(pk=self.filter['payer']) if self.filter['payer'] else None
            shipper = Org.objects.get(pk=self.filter['shipper']) if self.filter['shipper'] else None
            if payer or shipper:
                if payer:
                    q = q.filter(Q(bill__payer=payer) | Q(scan__payer=payer.name))
                if shipper:
                    q = q.filter(Q(bill__shipper=shipper) | Q(scan__shipper=shipper))
            else:
                q = q.all()
            q = q.order_by('-pk')    # [:100]
        else:
            q = q.none()
        # print q.query
        return q

    def get_context_data(self, **kwargs):
        context = super(LedgerList, self).get_context_data(**kwargs)
        context['ledger_lpp'] = self.paginate_by
        context['form'] = forms.FilterLedgerListForm(initial={
            'payer': self.filter['payer'],
            'shipper': self.filter['shipper'],
        })
        return context


@login_required
def ledger_set_lpp(request, lpp):
    request.session['ledger_lpp'] = int(lpp)
    return redirect('ledger_list')


@login_required
def ledger_set_filter(request):
    form = forms.FilterLedgerListForm(request.POST)
    if form.is_valid():
        filter = form.cleaned_data
        request.session['ledger_payer'] = filter['payer'].pk if filter['payer'] else None
        request.session['ledger_shipper'] = filter['shipper'].pk if filter['shipper'] else None
    return redirect('ledger_list')


class SummaryList(ListView):
    template_name = 'reports/summary_list.html'
    filter = {
        'place':    None,
        'subject':  None,
        'year':     None,
    }
    subjs = []
    subj = None

    def get_queryset(self):
        # print 'SummaryList.get_queryset in'
        self.filter['place'] = self.request.session.get('summary_place', None)
        self.filter['subject'] = self.request.session.get('summary_subject', None)
        self.filter['year'] = self.request.session.get('summary_year', None)
        # locals
        # print 'SummaryList.get_queryset init locals'
        p = self.filter['place']
        s = self.filter['subject']
        y = self.filter['year']
        # print 'SummaryList.get_queryset query create'
        # let's query
        #q = Scan.objects.values('place', 'subject', 'depart').filter(place=self.filter['place'], subject=self.filter['subject'], date__year=self.filter['year']).order_by('depart').annotate(Sum('sum'))
        # q = Place.objects.all()
        q = Scan.objects
        if (p and y):
            # print 'Filter:', p, y
            q = q.values('subject', 'depart').filter(place=p, date__year=y).order_by('subject', 'depart').annotate(Sum('sum'))
            # print 'Q:', q.query
        else:
            q = q.none()
        # print 'SummaryList.get_queryset out'
        return q

    def get_context_data(self, **kwargs):
        # print 'SummaryList.get_contextdata in'
        context = super(SummaryList, self).get_context_data(**kwargs)
        context['form'] = forms.FilterSummaryListForm(initial={
            'place':    self.filter['place'],
            'subject':  self.filter['subject'],
            'year':     self.filter['year'],
        })
        # print 'SummaryList.get_contextdata out'
        return context


@login_required
def summary_set_filter(request):
    # print 'summary_set_filter in'
    form = forms.FilterSummaryListForm(request.POST)
    if form.is_valid():
        filter = form.cleaned_data
        request.session['summary_place'] = filter['place'] if filter['place'] else None
        request.session['summary_subject'] = filter['subject'] if filter['subject'] else None
        request.session['summary_year'] = filter['year'] if filter['year'] else None
    # print 'summary_set_filter out'
    return redirect('summary_list')
