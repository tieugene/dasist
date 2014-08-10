# -*- coding: utf-8 -*-
'''
scan.views
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
import os, sys, imp, pprint, tempfile, subprocess, shutil, datetime, simplejson

# 3. 3rd party

# 4. my
import models, forms
from core.models import File, FileSeq, Org

reload(sys)
sys.setdefaultencoding('utf-8')

class	ScanDetail(DetailView):
	model = models.Scan
	template_name = 'scan/detail.html'

class	ScanList(ListView):
	template_name = 'scan/list.html'
	paginate_by = 25
	filter = {
		'place':	None,
		'subject':	None,
		'depart':	None,
		'supplier':	None,
		'billno':	None,
		'billdate':	None,
	}
	subjs = []
	subj = None

	def	get_queryset(self):
		#print 'ScanList get_queryset'
		# 1. handle session
		self.paginate_by = self.request.session.get('lpp', 25)
		self.filter['place'] =		self.request.session.get('scan_place', None)
		self.filter['subject'] =	self.request.session.get('scan_subject', None)
		self.filter['depart'] =		self.request.session.get('scan_depart', None)
		self.filter['supplier'] =	self.request.session.get('scan_supplier', None)
		self.filter['billno'] =		self.request.session.get('scan_billno', None)
		self.filter['billdate'] =	self.request.session.get('scan_billdate', None)
		# 2. create query
		q = models.Scan.objects.all()
		if self.filter['place']:
			q = q.filter(place=self.filter['place'])
			self.subjs = forms.EMPTY_VALUE + list(q.order_by('subject').distinct().exclude(subject=None).values_list('subject', 'subject'))
			if self.filter['subject']:
				self.subj = self.filter['subject']
				q = q.filter(subject=self.filter['subject'])
		if self.filter['depart']:
			q = q.filter(depart=self.filter['depart'])
		if self.filter['supplier']:
			q = q.filter(supplier=self.filter['supplier'])
		if self.filter['billno']:
			q = q.filter(no=self.filter['billno'])
		if self.filter['billdate']:
			#print "Filter by date:", self.filter['billdate'], type(self.filter['billdate'])
			#q = q.filter(date=self.filter['billdate'])
			try:
				q = q.filter(date=datetime.datetime.strptime(self.filter['billdate'], '%d.%m.%y'))
			except:
				pass
		return q

	def	get_context_data(self, **kwargs):
		#print 'ScanList get_context_data'
		context = super(ScanList, self).get_context_data(**kwargs)
		context['lpp']	= self.paginate_by
		context['form']	= forms.FilterScanListForm(initial={
			'place':	self.filter['place'],
			'subject':	self.filter['subject'],
			'depart':	self.filter['depart'],
			'supplier':	self.filter['supplier'],
			'billno':	self.filter['billno'],
			'billdate':	self.filter['billdate'],
		})
		#context['subjs']= self.subjs
		#context['subj']	= self.subj
		return context

def	scan_get_subjects(request):
	pass
	place=request.GET.get('place')
	ret=[dict(id='', value='---'),]
	if place:
		for subj in models.Scan.objects.filter(place=place).order_by('subject').distinct().exclude(subject=None).values_list('subject',):
			ret.append(dict(id=subj, value=subj))
	return HttpResponse(simplejson.dumps(ret), content_type='application/json')

@login_required
def	scan_set_lpp(request, lpp):
	request.session['lpp'] = int(lpp)
	return redirect('scan_list')

@login_required
def	scan_set_filter(request):
	form = forms.FilterScanListForm(request.POST)
	if form.is_valid():
		filter = form.cleaned_data
		#print "Set filter:", filter['billdate']
		request.session['scan_place'] =		filter['place']
		request.session['scan_subject'] =	filter['subject']
		request.session['scan_depart'] =	filter['depart']
		request.session['scan_supplier'] =	filter['supplier']
		request.session['scan_billno'] =	filter['billno']
		request.session['scan_billdate'] =	filter['billdate']
		#request.session['scan_billdate'] =	datetime.datetime.strptime(filter['billdate'], '%d.%m.%Y').date() if filter['billdate'] else None
	return redirect('scan_list')

@login_required
@transaction.commit_on_success
def	scan_edit(request, id):
	'''
	'''
	scan = models.Scan.objects.get(pk=int(id))
	if request.method == 'POST':
		form = forms.ScanEditForm(request.POST)
		if form.is_valid():
			suppinn = form.cleaned_data['suppinn'].strip()
			shippers = Org.objects.filter(inn=suppinn)
			if not len(shippers):	# not found > create
				shipper = Org(
					inn = suppinn,
					name = form.cleaned_data['suppname'].strip(),
					fullname = form.cleaned_data['suppfull'].strip()
				)
				shipper.save()
			else:
				shipper = shippers[0]
				form.cleaned_data['suppname'] = shipper.name
			scan.place	= form.cleaned_data['place'].strip()
			scan.subject	= form.cleaned_data['subject'].strip()
			scan.depart	= form.cleaned_data['depart'].strip()
			scan.payer	= form.cleaned_data['payer'].strip()
			scan.shipper	= shipper
			scan.supplier	= shipper.name
			scan.no		= form.cleaned_data['no'].strip()
			scan.date	= form.cleaned_data['date']
			scan.sum	= form.cleaned_data['sum']
			scan.save()
			return redirect('scan_view', scan.pk)
	else:
		form = forms.ScanEditForm(initial={
			'place': scan.place,
			'subject': scan.subject,
			'depart': scan.depart,
			'payer': scan.payer,
			'suppinn': scan.shipper.inn if scan.shipper else '',
			'suppname': scan.supplier,
			'suppfull': scan.shipper.fullname if scan.shipper else '',
			'no': scan.no,
			'date': scan.date,
			'sum': scan.sum,
		})
	return render_to_response('scan/form.html', context_instance=RequestContext(request, {
		'form': form,
		'object': scan,
	}))

@login_required
def	scan_delete(request, id):
	'''
	Delete bill
	ACL: (root|assignee) & (Draft|Rejected (bad))
	'''
	scan = models.Scan.objects.get(pk=int(id))
	scan.delete()
	fileseq.purge()
	return redirect('scan_list')

@login_required
def	scan_clean_spaces(request):
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
		if ((scan.place) and (scan.place != scan.place.strip())):	# scan.place, scan.subject, scan.depart, scan.no
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
			#print "need to save %d" % scan.pk
			#print "Place: '%s'" % scan.place
			scan.save()
		#print scan.place
	return redirect('scan_list')

@login_required
def	scan_replace_depart(request):
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
	return render_to_response('scan/form_replace_depart.html', context_instance=RequestContext(request, {
		'form': form,
		'msg': msg,
	}))

@login_required
def	scan_replace_place(request):
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
	return render_to_response('scan/form_replace_place.html', context_instance=RequestContext(request, {
		'form': form,
		'msg': msg,
	}))
