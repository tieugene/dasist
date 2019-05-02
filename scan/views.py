# -*- coding: utf-8 -*-
'''
scan.views
'''

# 1. system
import datetime
import json
import sys

# 2. my
from core.models import Org

# 3. django
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

try:
    import forms
except:
    print "Oops #1"

import models


reload(sys)
sys.setdefaultencoding('utf-8')


class ScanDetail(DetailView):
    model = models.Scan
    template_name = 'scan/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ScanDetail, self).get_context_data(**kwargs)
        context['prev'] = models.Scan.objects.filter(pk__lt=context['object'].pk).order_by('-pk').first()
        context['next'] = models.Scan.objects.filter(pk__gt=context['object'].pk).order_by('pk').first()
        return context


class ScanList(ListView):
    template_name = 'scan/list.html'
    paginate_by = 25
    filter = {
        'place':    None,
        'subject':  None,
        'depart':   None,
        'payer':    None,
        'shipper':  None,
        'billno':   None,
        'billdate': None,
    }
    subjs = []
    subj = None

    def get_queryset(self):
        # 1. handle session
        self.paginate_by = self.request.session.get('lpp', 25)
        self.filter['place'] = self.request.session.get('scan_place', None)
        self.filter['subject'] = self.request.session.get('scan_subject', None)
        self.filter['depart'] = self.request.session.get('scan_depart', None)
        self.filter['payer'] = self.request.session.get('scan_payer', None)
        self.filter['shipper'] = self.request.session.get('scan_shipper', None)
        self.filter['billno'] = self.request.session.get('scan_billno', None)
        self.filter['billdate'] = self.request.session.get('scan_billdate', None)
        # 2. create query
        q = models.Scan.objects.all().order_by('-pk')
        if self.filter['place']:
            q = q.filter(place=self.filter['place'])
            self.subjs = forms.EMPTY_VALUE + list(q.order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
            if self.filter['subject']:
                self.subj = self.filter['subject']
                q = q.filter(subject=self.filter['subject'])
        if self.filter['depart']:
            q = q.filter(depart=self.filter['depart'])
        if self.filter['payer']:
            q = q.filter(payer__contains=self.filter['payer'])
        if self.filter['shipper']:
            q = q.filter(shipper__pk=self.filter['shipper'])
        if self.filter['billno']:
            q = q.filter(no=self.filter['billno'])
        if self.filter['billdate']:
            # print "Filter by date:", self.filter['billdate'], type(self.filter['billdate'])
            # q = q.filter(date=self.filter['billdate'])
            try:
                q = q.filter(date=datetime.datetime.strptime(self.filter['billdate'], '%d.%m.%y'))
            except:
                pass
        return q

    def get_context_data(self, **kwargs):
        context = super(ScanList, self).get_context_data(**kwargs)
        context['lpp'] = self.paginate_by
        context['form'] = forms.FilterScanListForm(initial={
            'place':    self.filter['place'],
            'subject':  self.filter['subject'],
            'depart':   self.filter['depart'],
            'payer':    self.filter['payer'],
            'shipper':  self.filter['shipper'],
            'billno':   self.filter['billno'],
            'billdate': self.filter['billdate'],
        })
        # context['subjs']= self.subjs
        # context['subj']    = self.subj
        return context


def scan_get_subjects(request):
    '''
    AJAX callback
    '''
    place = request.GET.get('place')
    ret = [dict(id='', value='---'), ]
    if place:
        for subj in models.Scan.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject',):
            ret.append(dict(id=subj, value=subj))
    return HttpResponse(json.dumps(ret), content_type='application/json')


@login_required
def scan_set_lpp(request, lpp):
    request.session['lpp'] = int(lpp)
    return redirect('scan_list')


@login_required
def scan_set_filter(request):
    form = forms.FilterScanListForm(request.POST)
    if form.is_valid():
        filter = form.cleaned_data
        # print "Set filter:", filter['billdate']
        request.session['scan_place'] = filter['place']
        request.session['scan_subject'] = filter['subject']
        request.session['scan_depart'] = filter['depart']
        request.session['scan_payer'] = filter['payer']
        request.session['scan_shipper'] = filter['shipper'].pk if filter['shipper'] else None
        request.session['scan_billno'] = filter['billno']
        request.session['scan_billdate'] = filter['billdate']
        # request.session['scan_billdate'] =    datetime.datetime.strptime(filter['billdate'], '%d.%m.%Y').date() if filter['billdate'] else None
    return redirect('scan_list')


@login_required
@transaction.atomic
def scan_edit(request, id):
    '''
    '''
    scan = models.Scan.objects.get(pk=int(id))
    if request.method == 'POST':
        form = forms.ScanEditForm(request.POST)
        if form.is_valid():
            suppinn = form.cleaned_data['suppinn'].strip()
            shipper = Org.objects.filter(inn=suppinn).first()
            if not (shipper):    # not found > create
                shipper = Org(
                    inn=suppinn,
                    name=form.cleaned_data['suppname'].strip(),
                    fullname=form.cleaned_data['suppfull'].strip()
                )
                shipper.save()
            scan.place = form.cleaned_data['place'].strip()
            scan.subject = form.cleaned_data['subject'].strip()
            scan.depart = form.cleaned_data['depart'].strip()
            scan.payer = form.cleaned_data['payer'].strip()
            scan.shipper = shipper
            scan.supplier = shipper.name
            scan.no = form.cleaned_data['no'].strip()
            scan.date = form.cleaned_data['date']
            scan.sum = form.cleaned_data['sum']
            scan.save()
            return redirect('scan_view', scan.pk)
    else:
        form = forms.ScanEditForm(initial={
            'place':    scan.place,
            'subject':  scan.subject,
            'depart':   scan.depart,
            'payer':    scan.payer,
            'suppinn':  scan.shipper.inn if scan.shipper else '',
            'suppname': scan.shipper.name if scan.shipper else scan.supplier,
            'suppfull': scan.shipper.fullname if scan.shipper else '',
            'no':       scan.no,
            'date':     scan.date,
            'sum':      scan.sum,
        })
    return render(request, 'scan/form.html', {
        'form':        form,
        'object':    scan,
    })


@login_required
def scan_delete(request, id):
    '''
    Delete bill
    ACL: (root|assignee) & (Draft|Rejected (bad))
    '''
    if (request.user.is_superuser):
        scan = models.Scan.objects.get(pk=int(id))
        #scan.fileseq.purge()    # ???
        scan.delete()
    return redirect('scan_list')


@login_required
def scan_clean_spaces(request):
    '''
    place
    subject
    depart
    supplier
    no
    '''
    scans = models.Scan.objects.all()
    for scan in scans:
        tosave = False
        if ((scan.place) and (scan.place != scan.place.strip())):    # scan.place, scan.subject, scan.depart, scan.no
            scan.place = scan.place.strip()
            tosave |= True
        if ((scan.subject) and (scan.subject != scan.subject.strip())):
            scan.subject = scan.subject.strip()
            tosave |= True
        if ((scan.depart) and (scan.depart != scan.depart.strip())):
            scan.depart = scan.depart.strip()
            tosave |= True
        if ((scan.no) and (scan.no != scan.no.strip())):
            scan.no = scan.no.strip()
            tosave |= True
        if (tosave):
            # print "need to save %d" % scan.pk
            # print "Place: '%s'" % scan.place
            scan.save()
        # print scan.place
    return redirect('scan_list')


@login_required
def scan_replace_depart(request):
    if request.method == 'POST':
        form = forms.ReplaceDepartForm(request.POST)
        if form.is_valid():
            src = form.cleaned_data['src']
            dst = form.cleaned_data['dst']
            if src == dst:
                msg = 'Src == Dst'
            else:
                scans = models.Scan.objects.filter(depart=src)
                msg = '%d scans replaced' % scans.count()
                for scan in scans:
                    scan.depart = dst
                    scan.save()
    else:
        form = forms.ReplaceDepartForm()
        msg = None
    return render(request, 'scan/form_replace_depart.html', {
        'form': form,
        'msg': msg,
    })


@login_required
def scan_replace_place(request):
    msg = ''
    if request.method == 'POST':
        form = forms.ReplacePlaceForm(request.POST)
        if form.is_valid():
            src = form.cleaned_data['src']
            place = form.cleaned_data['place'].name
            subject = form.cleaned_data['subject'].name if form.cleaned_data['subject'] else None
            if src == place:
                msg = 'Src == Dst'
            else:
                scans = models.Scan.objects.filter(place=src)
                msg = '%d scans replaced' % scans.count()
                for scan in scans:
                    scan.place = place
                    if (subject):
                        scan.subject = subject
                    scan.save()
    else:
        form = forms.ReplacePlaceForm()
        msg = None
    return render(request, 'scan/form_replace_place.html', {
        'form': form,
        'msg': msg,
    })
