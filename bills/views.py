# -*- coding: utf-8 -*-
'''
TODO:
* get_object_or_404(
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.utils.datastructures import SortedDict
from django.db.models import F, Q
from django.core.files.storage import default_storage	# MEDIA_ROOT
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import send_mail
from django.core import serializers
from django.utils.encoding import smart_unicode
from django.db import transaction

# 2. system
import os, sys, imp, pprint, tempfile, subprocess, shutil, json, decimal
from django.utils import simplejson

# 3. 3rd party
#from pyPdf import PdfFileReader
#from pdfrw import PdfReader
from PIL import Image as PIL_Image
#from wand.image import Image as Wand_Image

# 4. my
import models, forms, utils
from core.models import File, FileSeq
from scan.models import Scan, Event

PAGE_SIZE = 20
FSNAME = 'fstate'	# 0..3

reload(sys)
sys.setdefaultencoding('utf-8')

def	__set_filter_state(q, s):
	'''
	q - original QuerySet (all)
	s - state (0..31; dead|done|onpay|onway|draft)
	'''
	retvalue = q
	if (not bool(s&1)):	# Rejected
		retvalue = retvalue.exclude(state__in = [3, 8])
	if (not bool(s&2)):	# Done
		retvalue = retvalue.exclude(state__in = [5, 9])
	if (not bool(s&4)):	# OnPay
		retvalue = retvalue.exclude(state = 4)
	if (not bool(s&8)):	# OnWay
		retvalue = retvalue.exclude(state__in = [2, 7])
	if (not bool(s&16)):	# Draft
		retvalue = retvalue.exclude(state__in = [1, 6])
	return retvalue

@login_required
def	bill_list(request):
	'''
	List of bills
	ACL: user=assign|approve|root
	'''
	# 1. pre
	user = request.user
	approver = models.Approver.objects.get(user=user)
	#print approver.role.pk == 1
	queryset = models.Bill.objects.all().order_by('-pk')
	# 2. mode (1=All, 2=Inbound)
	mode = request.session.get('mode', None)
	if (mode == None):
		mode = 1
		request.session['mode'] = mode
	else:
		mode = int(mode)
	# 3. filter by role
	role_id = approver.role.pk
	if (mode == 1):	# Все
		if (role_id == 1) and (not user.is_superuser):	# Исполнитель
			queryset = queryset.filter(assign=approver)
		elif (role_id == 3):	# Руководитель
			fsform = None
			b_list = models.Event.objects.filter(approve=approver).values_list('bill_id', flat=True)
			q1 = queryset.filter(rpoint__approve=approver)
			q2 = queryset.filter(pk__in=b_list)
			queryset = q1 | q2
		# 3. filter using Filter
		fsfilter = request.session.get(FSNAME, None)# int 0..15: dropped|done|onway|draft
		if (fsfilter == None):
			fsfilter = 31
			request.session[FSNAME] = fsfilter
		else:
			fsfilter = int(fsfilter)
		queryset = __set_filter_state(queryset, fsfilter)
		# 3. go
		#if not request.user.is_superuser:
		#	queryset = queryset.filter(assign=request.user)
		fsform = forms.FilterStateForm(initial={
			'dead'	:bool(fsfilter&1),
			'done'	:bool(fsfilter&2),
			'onpay'	:bool(fsfilter&4),
			'onway'	:bool(fsfilter&8),
			'draft'	:bool(fsfilter&16),
		})
	else:		# Входящие
		fsform = None
		if (approver.role.pk == 1):		# Исполнитель
			queryset = queryset.filter(assign=approver, rpoint=None)
		elif (approver.role.pk in set((4, 6))):	# Директор, Бухгалтер
			queryset = queryset.filter(rpoint__role=approver.role)
		else:
			queryset = queryset.filter(rpoint__approve=approver)
	# 4. lpp
	lpp = request.session.get('lpp', None)
	if (lpp == None):
		lpp = 20
		request.session['lpp'] = lpp
	else:
		lpp = int(lpp)
	return  object_list (
		request,
		queryset = queryset,
		paginate_by = lpp,
		page = int(request.GET.get('page', '1')),
		template_name = 'bills/list.html',
		extra_context = {
			'canadd': approver.canadd,
			'fsform': fsform,
			'lpp': lpp,
			'mode': mode,
			'role': approver.role,
		}
	)

@login_required
def	bill_filter_state(request):
	'''
	POST only
	* set filter in cookie
	* redirect
	'''
	fsform = forms.FilterStateForm(request.POST)
	if fsform.is_valid():
		fsfilter = \
			int(fsform.cleaned_data['dead'])  * 1 | \
			int(fsform.cleaned_data['done'])  * 2 | \
			int(fsform.cleaned_data['onpay']) * 4 | \
			int(fsform.cleaned_data['onway']) * 8 | \
			int(fsform.cleaned_data['draft']) * 16
		#print 'Filter:', fsfilter
		request.session[FSNAME] = fsfilter
	return redirect('bills.views.bill_list')

@login_required
def	bill_set_lpp(request, lpp):
	request.session['lpp'] = lpp
	return redirect('bills.views.bill_list')

@login_required
def	bill_set_mode(request, mode):
	request.session['mode'] = mode
	return redirect('bills.views.bill_list')

def	__pdf2png2(src_path, basename):
	tmpdir = tempfile.mkdtemp()
	# 1. extract
	arglist = ["gs", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pnggray", "-r150", "-sOutputFile=%s-%%d.png" % os.path.join(tmpdir, basename), src_path]
	sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	sp.communicate()
	# 2. mv
	retvalue = os.listdir(tmpdir)
	retvalue.sort()
	for f in retvalue:
		shutil.move(os.path.join(tmpdir, f), os.path.join(settings.MEDIA_ROOT, f))
	os.rmdir(tmpdir)
	return retvalue

def	__pdf2png3(src_path, basename):
	'''
	src_path - full path to src file
	basename - source file name w/o ext
	'''
	retvalue = list()
	tmpdir = tempfile.mkdtemp()
	# 1. extract
	arglist = ['pdfimages', '-q', '-j', src_path, os.path.join(tmpdir, basename)]
	sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	sp.communicate()
	# 2. convert
	filelist = os.listdir(tmpdir)
	filelist.sort()
	for f in filelist:
		chunk_path = os.path.join(tmpdir, f)
		with open(chunk_path, 'rb') as fh:
			img = PIL_Image.open(fh)
			name, ext = f.rsplit('.', 1)
			dst_filename = name + '.png'
			flag = {'jpg': 'L', 'ppm': 'L', 'pbm': '1'}[ext]
			img.convert('L').save(os.path.join(settings.MEDIA_ROOT, dst_filename), 'PNG')
			del img
			retvalue.append(dst_filename)
		os.unlink(chunk_path)
	os.rmdir(tmpdir)
	return retvalue

def	__convert_img(file, rawpdf=False):
	'''
	Convert image
	@param img:django.core.files.uploadedfile.InMemoryUploadedFile
	@return list of output filepaths
	'''
	retvalue = list()
	dirname = settings.MEDIA_ROOT
	filemime = file.content_type
	filename = file.name.encode('utf-8')
	src_path = os.path.join(settings.MEDIA_ROOT, filename)
	# beg
	#default_storage.save(filename, ContentFile(file.read()))	# unicode
	buffer = file.read()
	f = open(src_path, 'wb')
	f.write(buffer)
	f.close()
	# end
	basename = filename.rsplit('.', 1)[0]
	if (filemime == 'image/png'):
		img = PIL_Image.open(src_path)
		if (img.mode not in set(['1', 'L'])):	# [paletted ('P')], bw, grey
			img.convert('L').save(src_path)
		retvalue.append(filename)
	elif (filemime == 'image/jpeg'):
		img = PIL_Image.open(src_path)
		dst_filename = basename + '.png'
		img.convert('L').save(os.path.join(settings.MEDIA_ROOT, dst_filename), 'PNG')
		os.unlink(src_path)
		retvalue.append(dst_filename)
	elif (filemime == 'image/tiff'):
		img = PIL_Image.open(src_path)
		for i in range(9):
			try:
				img.seek(i)
				if (img.mode in set(['1','L'])):
					thumb = img
				else:
					thumb = img.convert('L')
				dst_filename = '%s-%d.png' % (basename, i+1)
				thumb.save(os.path.join(settings.MEDIA_ROOT, dst_filename), 'PNG')
				retvalue.append(dst_filename)
			except EOFError:
				break
		os.unlink(src_path)
	elif (filemime == 'application/pdf'):
		if (rawpdf):
			retvalue = __pdf2png2(src_path, basename)
		else:
			retvalue = __pdf2png3(src_path, basename)
		os.unlink(src_path)
	return retvalue

def	__update_fileseq(f, fileseq, rawpdf=False):
	for filename in __convert_img(f, rawpdf):
		src_path = os.path.join(settings.MEDIA_ROOT, filename)
		#myfile = File(file=SimpleUploadedFile(filename, default_storage.open(filename).read()))
		myfile = File(file=SimpleUploadedFile(filename, open(src_path).read()))	# unicode error
		myfile.save()
		#default_storage.delete(filename)
		os.unlink(src_path)
		fileseq.add_file(myfile)

@login_required
def	bill_add(request):
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
				place		= form.cleaned_data['place'],
				subject		= form.cleaned_data['subject'],
				depart		= form.cleaned_data['depart'],
				payer		= form.cleaned_data['payer'],
				supplier	= form.cleaned_data['supplier'],
				billno		= form.cleaned_data['billno'],
				billdate	= form.cleaned_data['billdate'],
				billsum		= form.cleaned_data['billsum'],
				payedsum	= form.cleaned_data['payedsum'],
				topaysum	= form.cleaned_data['topaysum'],
				assign		= approver,
				rpoint		= None,
				#done		= None,
				state		= models.State.objects.get(pk=1),
			)
			bill.save()
			# 4. add route
			std_route1 = [	# role_id, approve_id
				(2, models.Approver.objects.get(pk=23)),	# Gorbunoff.N.V.
				(3, form.cleaned_data['approver']),		# Руководитель
				(4, None),					# Директор
				(5, models.Approver.objects.get(pk=3)),		# Гендир
				#(6, models.Approver.objects.get(pk=4)),	# Бухгалтер
				(6, None),					# Бухгалтер
			]
			for i, r in enumerate(std_route1):
				bill.route_set.add(
					models.Route(
						bill	= bill,
						order	= i+1,
						role	= models.Role.objects.get(pk=r[0]),
						approve	= r[1],
					),
				)
			#bill = form.save(commit=False)
			return redirect('bills.views.bill_view', bill.pk)
	else:
		form = forms.BillAddForm()
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {
		'form': form,
		'places': models.Place.objects.all(),
	}))

@login_required
def	bill_edit(request, id):
	'''
	Update (edit) Draft bill
	ACL: (assignee) & Draft
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	#if (not request.user.is_superuser) and (\
	#   (bill.assign != approver) or\
	#   (bill.rpoint != None) or\
	#   (bill.done != None)):
	#	return redirect('bills.views.bill_view', bill.pk)
	if request.method == 'POST':
		form = forms.BillEditForm(request.POST, request.FILES)
		if form.is_valid():
			# 1. update bill
			bill.place =	form.cleaned_data['place']
			bill.subject =	form.cleaned_data['subject']
			bill.depart =	form.cleaned_data['depart']
			bill.payer =	form.cleaned_data['payer']
			bill.supplier =	form.cleaned_data['supplier']
			bill.billno =	form.cleaned_data['billno']
			bill.billdate =	form.cleaned_data['billdate']
			bill.billsum =	form.cleaned_data['billsum']
			bill.payedsum =	form.cleaned_data['payedsum']
			bill.topaysum =	form.cleaned_data['topaysum']
			bill.save()
			# 2. update approver (if required)
			special = bill.route_set.get(order=2)	# Аня
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
	else:	# GET
		form = forms.BillEditForm(initial={
			'place':	bill.place,
			'subject':	bill.subject,
			'depart':	bill.depart,
			'payer':	bill.payer,
			'supplier':	bill.supplier,
			'billno':	bill.billno,
			'billdate':	bill.billdate,
			'billsum':	bill.billsum,
			'payedsum':	bill.payedsum,
			'topaysum':	bill.topaysum,
			'approver':	bill.route_set.get(order=2).approve,	# костыль для initial
			#'approver':	6,
		})
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {
		'form': form,
		'object': bill,
		'places': models.Place.objects.all(),
	}))

@login_required
@transaction.commit_on_success
def	bill_reedit(request, id):
	'''
	Update (edit) Draft? bill
	ACL: (assignee) & Draft?
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	max_topaysum = bill.billsum - bill.payedsum
	if request.method == 'POST':
		form = forms.BillReEditForm(request.POST, max_topaysum = bill.billsum - bill.payedsum)
		if form.is_valid():
			# 1. update bill
			bill.topaysum =	form.cleaned_data['topaysum']
			bill.save()
			# 2. update approver (if required)
			special = bill.route_set.get(order=2)	# Аня
			if (special.approve != form.cleaned_data['approver']):
				special.approve = form.cleaned_data['approver']
				special.save()
			return redirect('bills.views.bill_view', bill.pk)
	else:	# GET
		form = forms.BillReEditForm(initial={
			'topaysum': bill.topaysum if bill.topaysum else max_topaysum,
			'approver':	bill.route_set.get(order=2).approve,
		})
	return render_to_response('bills/form_reedit.html', context_instance=RequestContext(request, {
		'form': form,
		'object': bill,
	}))

def	__mailto(request, bill):
	'''
	Sends emails to people:
	- onway - to rpoint role or aprove
	- Accept/Reject - to assignee
	@param bill:Bill
	'''
	def	__emailto(emails, bill_id, subj):
		if (emails):
			utils.send_mail(
				emails,
				'%s: %d' % (subj, bill_id),
				request.build_absolute_uri(reverse('bills.views.bill_view', kwargs={'id': bill_id})),
			)
	state = bill.get_state_id()
	if (state in set([2, 7])):	# OnWay
		subj = 'Новый счет на подпись'
		if (bill.rpoint.approve):
			emails = [bill.rpoint.approve.user.email]
		else:
			emails = list()
			for i in bill.rpoint.role.approver_set.all():
				emails.append(i.user.email)
		__emailto(emails, bill.pk, subj)
	elif (state in set([3, 8])):	# Reject
		__emailto([bill.assign.user.email], bill.pk, 'Счет завернут')
	elif (state == 5):		# Accepted
		__emailto([bill.assign.user.email], bill.pk, 'Счет оплачен')
	elif (state == 9):		# Accepted
		__emailto([bill.assign.user.email], bill.pk, 'Счет частично оплачен')

@login_required
@transaction.commit_on_success
def	bill_view(request, id):
	'''
	View/Accept/Reject bill
	ACL: (assignee & Draft & Route ok) | (approver & OnWay)
	TODO: подменить approver от root где только можно
	TODO: assignee+approver == bad way
	'''
	#bill = models.Bill.objects.get(pk=int(id))
	bill = get_object_or_404(models.Bill, pk=int(id))
	user = request.user
	approver = models.Approver.objects.get(user=user)
	bill_state_id = bill.get_state_id()
	form = None
	err = ''
	if (request.method == 'POST'):
		#if (request.POST['resume'] in set(['accept', 'reject'])) and (\
		#   ((bill_state_id == 1) and (approver == bill.assign)) or\
		#   (((bill_state_id == 2) or (bill_state_id == 3)) and ( \
		#	((bill.rpoint.approve != None) and (approver == bill.rpoint.approve)) or\
		#	((bill.rpoint.approve == None) and (approver.role == bill.rpoint.role))\
		#    ) \
		#    )
		#   ):
		if (True):	# dummy
			resume = (request.POST['resume'] == 'accept')
			form = forms.ResumeForm(request.POST)
			if form.is_valid():
				# 0. check prerequisites
				if (not resume) and (not form.cleaned_data['note']):				# resume not empty on reject
					err = 'Отказ необходимо комментировать'
				else:
					# 1. new comment
					models.Event.objects.create(
						bill=bill,
						approve=approver,
						resume=resume,
						comment=form.cleaned_data['note']
					)
					# 2. update bill
					if resume:	# Ok
						route_list = bill.route_set.all().order_by('order')
						if (bill_state_id in set([1, 6])):	# 1. 1st (draft)
							bill.rpoint = route_list[0]
							if (bill_state_id == 1):	# draft
								bill.set_state_id(2)
							else:				# draft?
								bill.set_state_id(7)
						elif (bill_state_id in set([2, 7])):	# 2. onway
							rpoint = bill.rpoint
							if (rpoint.order == len(route_list)):	# 2. last (accounter)
								bill.set_state_id(4)
							else:					# 3. intermediate
								bill.rpoint = bill.route_set.get(order=rpoint.order+1)
						elif (bill_state_id == 4):	# OnPay
							bill.rpoint = None
							bill.payedsum += bill.topaysum
							bill.topaysum = decimal.Decimal('0.00')
							if (bill.payedsum == bill.billsum):
								bill.set_state_id(5)
							else:
								bill.set_state_id(9)
					else:		# Reject
						bill.rpoint = None
						if (bill_state_id == 2):
							# TODO: duplication
							bill.set_state_id(3)
						else:	# 7
							bill.set_state_id(8)
					bill.save()
					if (bill.get_state_id() == 5):	# That's all
						bill.rpoint = bill.route_set.all().delete()
					__mailto(request, bill)
					return redirect('bills.views.bill_list')
	if (form == None):
		form = forms.ResumeForm()
	buttons = {
		'edit':		# assignee & Draft*
			(user.is_superuser or ((bill.assign == approver) and (bill_state_id in set([1, 6])))),
		'del':		# assignee & (Draft|Rejected)
			(user.is_superuser or ((bill.assign == approver) and (bill_state_id in set([1, 3])))),
		'restart':	# assignee & (Rejected*|Done?)
			(user.is_superuser or ((bill.assign == approver) and (bill_state_id in set([3, 8, 9])))),
		'arch':		# assignee & Done
			(user.is_superuser or ((bill.assign == approver) and (bill_state_id == 5))),
	}
	# Accepting (Вперед, Согласовано, В оплате, Исполнено)
	buttons['accept'] = 0
	if (bill_state_id in set([1, 6])):		# Draft
		if (bill.assign == approver):
			buttons['accept'] = 1		# Вперед
	elif (bill_state_id in set([2, 7])):		# OnWay
		if (approver.role.pk != 6):		# not Accounter
			if ((bill.rpoint.approve == None) and (bill.rpoint.role == approver.role)) or \
			   ((bill.rpoint.approve != None) and (bill.rpoint.approve == approver)):
				buttons['accept'] = 2		# Согласовано
		else:					# Accounter
			buttons['accept'] = 3		# В оплате
	elif (bill_state_id == 4):			# OnPay
		if (approver.role.pk == 6):		# Accounter
			buttons['accept'] = 4		# Оплачен
	# Rejecting (Отказать, Дубль)
	buttons['reject'] = 0
	if (bill_state_id in set([2, 7])):		# OnWay
		if (approver.role.pk != 6):
			if ((bill.rpoint.approve == None) and (bill.rpoint.role == approver.role)) or \
			   ((bill.rpoint.approve != None) and (bill.rpoint.approve == approver)):
				buttons['reject'] = 1	# Отказать
		else:
			if (bill.get_state_id() == 2) and (bill.rpoint.role == approver.role):
				buttons['reject'] = 2	# Дубль
	return render_to_response('bills/detail.html', context_instance=RequestContext(request, {
		'object': bill,
		'form': form if (buttons['accept'] or buttons['reject']) else None,
		'err': err,
		'button': buttons,
	}))

@login_required
@transaction.commit_on_success
def	bill_delete(request, id):
	'''
	Delete bill
	ACL: (root|assignee) & (Draft|Rejected (bad))
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() in set([1, 3]) )):
		fileseq = bill.fileseq
		bill.delete()
		fileseq.purge()
		return redirect('bills.views.bill_list')
	else:
		return redirect('bills.views.bill_view', bill.pk)

@login_required
@transaction.commit_on_success
def	bill_restart(request, id):
	'''
	Restart bill
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() in set([3, 8, 9]))):
		if (bill.get_state_id() == 3):
			bill.set_state_id(1)
		else:
			bill.set_state_id(6)
		bill.save()
	return redirect('bills.views.bill_view', bill.pk)

@login_required
def	mailto(request, id):
	'''
	@param id: bill id
	'''
	bill = models.Bill.objects.get(pk=int(id))
	utils.send_mail(
		['ti.eugene@gmail.com'],
		'Новый счет на подпись: %s' % id,
		'Вам на подпись поступил новый счет: %s' % request.build_absolute_uri(reverse('bills.views.bill_view', kwargs={'id': bill.pk})),
	)
	return redirect('bills.views.bill_view', bill.pk)

@login_required
@transaction.commit_on_success
def	bill_toscan(request, id):
	'''
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() == 5)):
		scan = Scan.objects.create(
			fileseq	= bill.fileseq,
			place	= bill.place.name,
			subject	= bill.subject.name if bill.subject else None,
			depart	= bill.depart.name if bill.depart else None,
			payer	= bill.payer.name if bill.payer else None,
			supplier= bill.supplier,
			no	= bill.billno,
			date	= bill.billdate,
			sum	= bill.billsum,
		)
		for event in (bill.events.all()):
			Event.objects.create(
				scan=scan,
				approve='%s %s (%s)' % (event.approve.user.last_name, event.approve.user.first_name, event.approve.jobtit),
				resume=event.resume,
				ctime=event.ctime,
				comment=event.comment
			)
		bill.delete()
		return redirect('bills.views.bill_list')
	else:
		return redirect('bills.views.bill_view', bill.pk)
