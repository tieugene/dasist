# -*- coding: utf-8 -*-
'''
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.utils.datastructures import SortedDict
from django.db.models import F
from django.core.files.storage import default_storage	# MEDIA_ROOT

# 2. system
import os, sys, imp, pprint, tempfile, subprocess, shutil

# 3. 3rd party

# 4. my
import models, forms
from core.models import File, FileSeq

reload(sys)
sys.setdefaultencoding('utf-8')

@login_required
def	scan_list(request):
	'''
	'''
	# 1. pre
	user = request.user
	# 2. lpp
	lpp = int(request.session.get('lpp', 20))
	# 3. get values
	filter = {
		'place':	request.session.get('scan_place', None),
		'depart':	request.session.get('scan_depart', None),
		'supplier':	request.session.get('scan_supplier', None),
		'billno':	request.session.get('scan_billno', None),
		'billdate':	request.session.get('scan_billdate', None),
	}
	# 4. set filter values
	if request.method == 'POST':
		form = forms.FilterScanListForm(request.POST)
		if form.is_valid():
			# 4.1. get values
			filter = {
				'place':	form.cleaned_data['place'],
				'depart':	form.cleaned_data['depart'],
				'supplier':	form.cleaned_data['supplier'],
				'billno':	form.cleaned_data['billno'],
				'billdate':	form.cleaned_data['billdate'],
			}
			# 4.2. set session values
			request.session['scan_place'] =		filter['place']
			request.session['scan_depart'] =	filter['depart']
			request.session['scan_supplier'] =	filter['supplier']
			request.session['scan_billno'] =	filter['billno']
			request.session['scan_billdate'] =	filter['billdate']
		else:
			print 'Invalid form'
	# 5. set default form values
	else:
		# 3.2.2. gen form
		form = forms.FilterScanListForm(initial={
			'place':	filter['place'],
			'depart':	filter['depart'],
			'supplier':	filter['supplier'],
			'billno':	filter['billno'],
			'billdate':	filter['billdate'],
		})
	# 6. filter
	#print 'Place:', filter['place']
	q = models.Scan.objects.all()
	if filter['place']:
		q = q.filter(place=filter['place'])
	if filter['depart']:
		q = q.filter(depart=filter['depart'])
	if filter['supplier']:
		q = q.filter(supplier=filter['supplier'])
	if filter['billno']:
		q = q.filter(no=filter['billno'])
	if filter['billdate']:
		q = q.filter(date=filter['billdate'])
	return  object_list (
		request,
		queryset = q,
		paginate_by = lpp,
		page = int(request.GET.get('page', '1')),
		template_name = 'scan/list.html',
		extra_context = {
			'lpp': lpp,
			'form': form,
		}
	)

@login_required
def	scan_set_lpp(request, lpp):
	request.session['lpp'] = lpp
	return redirect('scan.views.scan_list')

@login_required
def	scan_add(request):
	'''
	Add new (draft) bill
	ACL: Исполнитель
	- add Bill
	- add Route to them
	- convert image
	- add images into fileseq
	'''
	user = request.user
	#approver = models.Approver.objects.get(pk=user.pk)	# !!!
	approver = models.Approver.objects.get(user=user)	# !!!
	#if not user.is_superuser:
	#	if (approver.role.pk != 1):
	#		return redirect('bills.views.bill_list')
	if request.method == 'POST':
		#path = request.POST['path']
		form = forms.BillAddForm(request.POST, request.FILES)
		if form.is_valid():
			# 1. create fileseq
			fileseq = FileSeq()
			fileseq.save()
			# 2. convert image and add to fileseq
			__update_fileseq(request.FILES['file'], fileseq, form.cleaned_data['rawpdf'])
			# 3. bill at all
			bill = models.Bill(
				fileseq		= fileseq,
				project		= form.cleaned_data['project'],
				depart		= form.cleaned_data['depart'],
				supplier	= form.cleaned_data['supplier'],
				assign		= approver,
				rpoint		= None,
				done		= None,
			)
			bill.save()
			# 4. add route
			std_route1 = [	# role_id, approve_id, state_id, button_title
				(2, models.Approver.objects.get(pk=13), 1, 'Ok'),	# начОМТС
				(3, form.cleaned_data['approver'], 1, 'Ok'),		# Руководитель
				(4, None, 1, 'Ok'),					# Директор
				(5, models.Approver.objects.get(pk=3), 1, 'Согласовано'),	# Гендир
				#(6, models.Approver.objects.get(pk=4), 2, 'Oплачено'),	# Бухгалтер
				(6, None, 2, 'Oплачено'),	# Бухгалтер
			]
			for i, r in enumerate(std_route1):
				bill.route_set.add(
					models.Route(
						bill	= bill,
						order	= i+1,
						role	= models.Role.objects.get(pk=r[0]),
						approve	= r[1],
						state	= models.State.objects.get(pk=r[2]),
						action	= r[3],
					),
				)
			#bill = form.save(commit=False)
			return redirect('bills.views.bill_view', bill.pk)
	else:
		form = forms.BillAddForm()
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {'form': form,}))

@login_required
def	scan_edit(request, id):
	'''
	Update (edit) scan
	Nothing works
	ACL: (assignee) & Draft
	'''
	user = request.user
	#approver = models.Approver.objects.get(pk=user.pk)
	bill = models.Bill.objects.get(pk=int(id))
	#if (not request.user.is_superuser) and (\
	#   (bill.assign != approver) or\
	#   (bill.rpoint != None) or\
	#   (bill.done != None)):
	#	return redirect('bills.views.bill_view', bill.pk)
	if request.method == 'POST':
		form = forms.BillEditForm(request.POST, request.FILES)
		if form.is_valid():
			tosave = False
			# 1. update bill
			if (bill.project != form.cleaned_data['project']):
				bill.project = form.cleaned_data['project']
				tosave = True
			if (bill.depart != form.cleaned_data['depart']):
				bill.depart = form.cleaned_data['depart']
				tosave = True
			if (bill.supplier != form.cleaned_data['supplier']):
				bill.supplier = form.cleaned_data['supplier']
				tosave = True
			if (tosave):
				bill.save()
			# 2. update approver (if required)
			special = bill.route_set.get(order=2)
			if (special.approve != form.cleaned_data['approver']):
				special.approve = form.cleaned_data['approver']
				special.save()
			# 3. update image
			file = request.FILES.get('file', None)
			if (file):
				fileseq = bill.fileseq
				fileseq.clean_children()
				__update_fileseq(file, fileseq, form.cleaned_data['rawpdf'])	# unicode error
			return redirect('bills.views.bill_view', bill.pk)
	else:
		form = forms.BillEditForm(initial={
			'project':	bill.project,
			'depart':	bill.depart,
			'supplier':	bill.supplier,
			#'approver':	6,
		})
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {
		'form': form,
		'object': bill,
	}))

@login_required
def	scan_view(request, id):
	return  object_detail (
		request,
		queryset = models.Scan.objects.all(),
		object_id = id,
		template_name = 'scan/detail.html',
	)

@login_required
def	scan_delete(request, id):
	'''
	Delete bill
	ACL: (root|assignee) & (Draft|Rejected (bad))
	'''
	scan = models.Scan.objects.get(pk=int(id))
	scan.delete()
	fileseq.purge()
	return redirect('scan.views.scan_list')

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
	return redirect('scan.views.scan_list')

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
