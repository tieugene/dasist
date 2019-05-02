# -*- coding: utf-8 -*-
'''
contrarch.views
'''

# 1. system
import datetime
import json
import sys

# 2. my

# 3. django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

try:
    import forms
except:
    print "Oops #2"

import models


reload(sys)
sys.setdefaultencoding('utf-8')


class ContrarchDetail(DetailView):
    model = models.Contrarch
    template_name = 'contrarch/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ContrarchDetail, self).get_context_data(**kwargs)
        context['prev'] = models.Contrarch.objects.filter(pk__lt=context['object'].pk).order_by('-pk').first()
        context['next'] = models.Contrarch.objects.filter(pk__gt=context['object'].pk).order_by('pk').first()
        return context


class ContrarchList(ListView):
    template_name = 'contrarch/list.html'
    paginate_by = 25
    filter = {
        'place':    None,
        'subject':  None,
        'customer':   None,
        'depart':   None,
        'payer':    None,
        'shipper':  None,
        'docno':   None,
        'docdate': None,
    }
    subjs = []
    subj = None

    def get_queryset(self):
        # 1. handle session
        self.paginate_by = self.request.session.get('lpp', 25)
        self.filter['place'] = self.request.session.get('contrarch_place', None)
        self.filter['subject'] = self.request.session.get('contrarch_subject', None)
        self.filter['customer'] = self.request.session.get('contrarch_customer', None)
        self.filter['depart'] = self.request.session.get('contrarch_depart', None)
        self.filter['payer'] = self.request.session.get('contrarch_payer', None)
        self.filter['shipper'] = self.request.session.get('contrarch_shipper', None)
        self.filter['docno'] = self.request.session.get('contrarch_docno', None)
        self.filter['docdate'] = self.request.session.get('contrarch_docdate', None)
        # 2. create query
        q = models.Contrarch.objects.all().order_by('-pk')
        if self.filter['place']:
            q = q.filter(place=self.filter['place'])
            self.subjs = forms.EMPTY_VALUE + list(q.order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
            if self.filter['subject']:
                self.subj = self.filter['subject']
                q = q.filter(subject=self.filter['subject'])
        if self.filter['customer']:
            q = q.filter(customer=self.filter['customer'])
        if self.filter['depart']:
            q = q.filter(depart=self.filter['depart'])
        if self.filter['payer']:
            q = q.filter(payer__contains=self.filter['payer'])
        if self.filter['shipper']:
            q = q.filter(shipper__pk=self.filter['shipper'])
        if self.filter['docno']:
            q = q.filter(no=self.filter['docno'])
        if self.filter['docdate']:
            # print "Filter by date:", self.filter['docdate'], type(self.filter['docdate'])
            # q = q.filter(date=self.filter['docdate'])
            try:
                q = q.filter(date=datetime.datetime.strptime(self.filter['docdate'], '%d.%m.%y'))
            except:
                pass
        return q

    def get_context_data(self, **kwargs):
        context = super(ContrarchList, self).get_context_data(**kwargs)
        context['lpp'] = self.paginate_by
        context['form'] = forms.FilterContrarchListForm(initial={
            'place':    self.filter['place'],
            'subject':  self.filter['subject'],
            'customer':   self.filter['customer'],
            'depart':   self.filter['depart'],
            'payer':    self.filter['payer'],
            'shipper':  self.filter['shipper'],
            'docno':   self.filter['docno'],
            'docdate': self.filter['docdate'],
        })
        # context['subjs']= self.subjs
        # context['subj']    = self.subj
        return context


def contrarch_get_subjects(request):
    '''
    AJAX callback
    '''
    place = request.GET.get('place')
    ret = [dict(id='', value='---'), ]
    if place:
        for subj in models.Contrarch.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject',):
            ret.append(dict(id=subj, value=subj))
    return HttpResponse(json.dumps(ret), content_type='application/json')


@login_required
def contrarch_set_lpp(request, lpp):
    request.session['lpp'] = int(lpp)
    return redirect('contrarch_list')


@login_required
def contrarch_set_filter(request):
    form = forms.FilterContrarchListForm(request.POST)
    if form.is_valid():
        filter = form.cleaned_data
        request.session['contrarch_place'] = filter['place']
        request.session['contrarch_subject'] = filter['subject']
        request.session['contrarch_customer'] = filter['customer']
        request.session['contrarch_depart'] = filter['depart']
        request.session['contrarch_payer'] = filter['payer']
        request.session['contrarch_shipper'] = filter['shipper'].pk if filter['shipper'] else None
        request.session['contrarch_docno'] = filter['docno']
        request.session['contrarch_docdate'] = filter['docdate']
    return redirect('contrarch_list')
