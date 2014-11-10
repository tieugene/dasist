# -*- coding: utf-8 -*-
'''
bills.views
'''

# 1. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.template import RequestContext, Context, loader
from django.views.generic import ListView, DetailView
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
import sys, pprint, decimal

# 4. my
import models, forms
from core.models import File, FileSeq, FileSeqItem, Org
from scan.models import Scan, Event
from views_extras import *

import logging
logger = logging.getLogger(__name__)

PAGE_SIZE = 25
FSNAME = 'fstate'	# 0..3

STATE_DRAFT	= 1
STATE_ONWAY	= 2
STATE_REJECTED	= 3
STATE_ONPAY	= 4
STATE_DONE	= 5

reload(sys)
sys.setdefaultencoding('utf-8')

class	BillList(ListView):
	'''
	ACL:
	- All:
	-- Исполнитель: только свои (где он - Исполнитель)
	-- Руководитель: только где он - текущий Подписант или в Истории
	-- *: все
	- Inboud:
	-- Испольнитель: только свои И без подписанта (== Черновик, Завернут, Исполнен)
	-- Директор, Бухгалтер = где роль тек. Подписанта == роль юзверя
	-- *: == тек. Подписант

	'''
	template_name = 'bills/list.html'
	paginate_by = PAGE_SIZE
	# custom:
	approver = None
	mode = None
	fsfilter = None

	def	get_queryset(self):
		# 1. vars
		self.paginate_by = self.request.session.get('lpp', 25)
		user = self.request.user
		self.approver = models.Approver.objects.get(user=user)	# user as approver
		role_id = self.approver.role.pk				# user's role
		self.mode = int(self.request.session.get('mode', 1))
		self.fsfilter = self.request.session.get(FSNAME, 31)	# default == all
		# 2. query
		q = models.Bill.objects.all().order_by('-pk')
		if (self.mode == 1):	# Everything
			if (role_id == 1) and (not user.is_superuser):	# Исполнитель
				q = q.filter(assign=self.approver)
			elif (role_id == 3):				# Руководитель
				self.fsform = None
				b_list = models.Event.objects.filter(approve=self.approver).values_list('bill_id', flat=True)
				q1 = q.filter(rpoint__approve=self.approver)
				q2 = q.filter(pk__in=b_list)
				q = q1 | q2
			# 3. filter using Filter
			fsfilter = self.request.session.get(FSNAME, None)
			if (fsfilter == None):
				fsfilter = 31	# default == all
				self.request.session[FSNAME] = fsfilter
			else:
				fsfilter = int(fsfilter)
			q = set_filter_state(q, fsfilter)
			# 3. go
			self.fsform = forms.FilterStateForm(initial={
				'dead'	:bool(fsfilter&1),
				'done'	:bool(fsfilter&2),
				'onpay'	:bool(fsfilter&4),
				'onway'	:bool(fsfilter&8),
				'draft'	:bool(fsfilter&16),
			})
		else:			# Inbound
			self.fsform = None
			if (role_id == 1):		# Исполнитель
				q = q.filter(assign=self.approver, rpoint=None)
			elif (role_id in set((4, 6))):	# Директор, Бухгалтер
				q = q.filter(rpoint__role=self.approver.role)
			else:
				q = q.filter(rpoint__approve=self.approver)
		return q

	def	get_context_data(self, **kwargs):
		context = super(BillList, self).get_context_data(**kwargs)
		context['lpp']		= self.paginate_by
		context['role']		= self.approver.role
		context['canadd']	= self.approver.canadd
		context['mode']		= self.mode
		context['fsform']	= self.fsform
		return context

@login_required
def	bill_filter_state(request):
	'''
	Set filter on state of bill list
	POST only
	* set filter in cookie
	* redirect
	ACL: *
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
	return redirect('bill_list')

@login_required
def	bill_set_lpp(request, lpp):
	'''
	Set lines-per-page of bill list.
	ACL: *
	'''
	request.session['lpp'] = lpp
	return redirect('bill_list')

@login_required
def	bill_set_mode(request, mode):
	'''
	Set bill list mode (all/inbound)
	ACL: *
	'''
	request.session['mode'] = mode
	return redirect('bill_list')

@login_required
@transaction.atomic
def	bill_add(request):
	'''
	Add new (draft) bill
	ACL: Исполнитель
	'''
	user = request.user
	approver = models.Approver.objects.get(user=user)
	if (approver.role.pk != 1):
		return redirect('bill_list')
	if request.method == 'POST':
		#path = request.POST['path']
		form = forms.BillAddForm(request.POST, request.FILES)
		if form.is_valid():
			# FIXME: add transaction
			# 1. create fileseq
			fileseq = FileSeq.objects.create()
			# 2. convert image and add to fileseq
			update_fileseq(request.FILES['file'], fileseq, form.cleaned_data['rawpdf'])
			# 3. bill at all
			shipper = handle_shipper(form)
			bill = models.Bill.objects.create(
				fileseq		= fileseq,
				place		= form.cleaned_data['place'],
				subject		= form.cleaned_data['subject'],
				depart		= form.cleaned_data['depart'],
				payer		= form.cleaned_data['payer'],
				shipper		= shipper,
				supplier	= shipper.name,
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
			# 4. add route
			mgr = form.cleaned_data['approver']
			fill_route(bill, mgr)
			return redirect('bills.views.bill_view', bill.pk)
	else:
		form = forms.BillAddForm()
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {
		'form': form,
		'places': models.Place.objects.all(),
	}))

@login_required
@transaction.atomic
def	bill_edit(request, id):
	'''
	Update (edit) Draft bill
	ACL: root | (Испольнитель & Draft & !Locked)
	TODO: transaction
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))	# FIXME: select_for_update(nowait=False)
	#bill = models.Bill.objects.get(pk=int(id))
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	if not (request.user.is_superuser or (\
	   (bill.assign == approver) and\
	   (bill.get_state_id() == 1) and\
	   (not bill.locked))):
		return redirect('bills.views.bill_view', bill.pk)
	if request.method == 'POST':
		form = forms.BillEditForm(request.POST, request.FILES)
		if form.is_valid():
			# FIXME: add transaction
			shipper = handle_shipper(form)
			# 1. update bill
			bill.place =	form.cleaned_data['place']
			bill.subject =	form.cleaned_data['subject']
			bill.depart =	form.cleaned_data['depart']
			bill.payer =	form.cleaned_data['payer']
			bill.shipper =	shipper
			bill.supplier =	shipper.name
			bill.billno =	form.cleaned_data['billno']
			bill.billdate =	form.cleaned_data['billdate']
			bill.billsum =	form.cleaned_data['billsum']
			bill.payedsum =	form.cleaned_data['payedsum']
			bill.topaysum =	form.cleaned_data['topaysum']
			bill.save()	# FIXME: update()
			# 2. update approver (if required)
			special = bill.route_set.get(order=2)	# OMTS boss
			if (special.approve != form.cleaned_data['approver']):
				special.approve = form.cleaned_data['approver']
				special.save()
			# 3. update image
			file = request.FILES.get('file', None)
			if (file):
				fileseq = bill.fileseq
				fileseq.clean_children()
				update_fileseq(file, fileseq, form.cleaned_data['rawpdf'])	# unicode error
			return redirect('bills.views.bill_view', bill.pk)
	else:	# GET
		form = forms.BillEditForm(initial={
			'place':	bill.place,
			'subject':	bill.subject,
			'depart':	bill.depart,
			'payer':	bill.payer,
			'suppinn':	bill.shipper.inn if bill.shipper else '',
			'suppname':	bill.shipper.name if bill.shipper else bill.supplier,
			'suppfull':	bill.shipper.fullname if bill.shipper else '',
			'billno':	bill.billno,
			'billdate':	bill.billdate,
			'billsum':	bill.billsum,
			'payedsum':	bill.payedsum,
			'topaysum':	bill.topaysum,
			'approver':	bill.route_set.get(order=2).approve,	# костыль для initial
			#'approver':	6,
		})
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {
		'form':		form,
		'object':	bill,
		'places':	models.Place.objects.all(),
	}))

@login_required
@transaction.atomic
def	bill_reedit(request, id):
	'''
	Update (edit) locked Draft bill
	ACL: root | (Испольнитель & Draft & Locked)
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	if not (request.user.is_superuser or (\
	   (bill.assign == approver) and\
	   (bill.get_state_id() == 1) and\
	   (bill.locked))):
		return redirect('bills.views.bill_view', bill.pk)
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
		# hack
		if (bill.route_set.count() == 0):
			#print "Fill route"
			mgr = models.Approver.objects.get(pk=9)
			fill_route(bill, mgr)
		# /hack
		form = forms.BillReEditForm(initial={
			'topaysum': bill.topaysum if bill.topaysum else max_topaysum,
			'approver':	bill.route_set.get(order=2).approve,
		})
	return render_to_response('bills/form_reedit.html', context_instance=RequestContext(request, {
		'form': form,
		'object': bill,
	}))

@login_required
@transaction.atomic
def	bill_view(request, id, upload_form=None):
	'''
	View | Accept/Reject bill
	ACL: (assignee & Draft & Route ok) | (approver & OnWay)
	- POST (Draft)
	-- Исполнитель & Draft
	-- Руководитель & Подписант онже [& Onway]
	-- Директор & Подписант.Роль егоже [& Onway]
	-- Бухгалтер & Подписант.Роль [& (Onway/Onpay)]
	-- Гендир & Подписант онже [& Onway]
	- POST (upload):
	-- user == Исполнитель & Draft
	- POST
	-- user == Исполнитель & Draft
	-- user.role == Директор | Бухгалтер == Подписант.Роль
	-- user == Подписант
	- GET
	-- root
	-- Исполнитель: user == Исполнитель
	-- Руководитель: user == Подписант или в Истории
	-- *: все
	'''
	def	__can_upload(bill, approver):
		'''
		ACL to uppload img.
		user == bill.approver && bill.state == Draft
		'''
		return (approver == bill.assign) and (bill.get_state_id() == 1)

	def	__upload(request, bill):
		'''
		Upload file to Bill
		@param request
		@parma bill:models.Bill
		@return upload_form
		'''
		upload_form = forms.BillAddFileForm(request.POST, request.FILES)
		if upload_form.is_valid():
			file = request.FILES.get('file', None)
			if (file):
				fileseq = bill.fileseq
				update_fileseq(file, fileseq, upload_form.cleaned_data['rawpdf'])	# unicode error
		return upload_form
	def	__can_resume(request, bill, approver):
		'''
		ACL to resume.
		- Draft and user == bill assign
		- OnWay and ((user == bill.rpoint.user) or (user.role == bill.rpoint.role))
		- OnPay and user.role == Accounter
		'''
		bill_state_id = bill.get_state_id()
		return (request.POST['resume'] in set(['accept', 'reject'])) and (\
		  ((bill_state_id == STATE_DRAFT) and (approver == bill.assign)) or \
		  ((bill_state_id == STATE_ONWAY) and ( \
			((bill.rpoint.approve != None) and (approver == bill.rpoint.approve)) or\
			((bill.rpoint.approve == None) and (approver.role == bill.rpoint.role))\
		   ) \
		  ) or \
		  ((bill_state_id == STATE_ONPAY) and (approver.role == bill.rpoint.role)) \
		)

	def	__resume(request, bill):
		'''
		@return resume_form, err[, redirect[ url]
		'''
		approver = models.Approver.objects.get(user=request.user)
		bill_state_id = bill.get_state_id()
		ok = False
		err = None
		resume_form = forms.ResumeForm(request.POST)
		if resume_form.is_valid():
			resume = (request.POST['resume'] == 'accept')
			# 0. check prerequisites
			if (not resume) and (not resume_form.cleaned_data['note']):			# resume not empty on reject
				err = 'Отказ необходимо комментировать'
			else:
				# 1. new comment
				models.Event.objects.create(
					bill=bill,
					approve=approver,
					resume=resume,
					comment=resume_form.cleaned_data['note']
				)
				# 2. update bill
				if resume:	# Ok
					route_list = bill.route_set.all().order_by('order')
					if (bill_state_id == 1):	# 1. 1st (draft)
						bill.rpoint = route_list[0]
						bill.set_state_id(2)
					elif (bill_state_id == 2):	# 2. onway
						rpoint = bill.rpoint
						if (rpoint.order == len(route_list)):	# 2. last (accounter)
							bill.set_state_id(4)
						else:					# 3. intermediate
							bill.rpoint = bill.route_set.get(order=rpoint.order+1)
					elif (bill_state_id == 4):	# OnPay
						bill.rpoint = None
						bill.payedsum += bill.topaysum
						bill.topaysum = decimal.Decimal('0.00')
						bill.set_state_id(5)
						bill.locked = (bill.payedsum < bill.billsum)
				else:		# Reject
					bill.set_state_id(3)
					bill.rpoint = None
				bill.save()
				if (bill.get_state_id() == 5) and (bill.locked == False):	# That's all
					bill.route_set.all().delete()
				mailto(request, bill)
				ok = True
		return (ok, resume_form, err)
	def	__can_accept():
		pass
	def	__accept():
		pass
	def	__can_reject():
		pass
	def	__reject():
		pass
	bill = get_object_or_404(models.Bill, pk=int(id))
	user = request.user
	logger.info('bill_view: user: %s, bill: %s' % (user.username, id))
	approver = models.Approver.objects.get(user=user)
	bill_state_id = bill.get_state_id()
	upload_form = None
	resume_form = None
	err = ''
	if (request.method == 'POST'):
		if request.POST['action'] == 'upload':
			if (__can_upload(bill, approver)):
				upload_form = __upload(request, bill)
		else:	# resume
			if (__can_resume(request, bill, approver)):
				ok, resume_form, err = __resume(request, bill)
				if (ok):
					return redirect('bill_list')
	else:	# GET
		if (user.is_superuser or ((bill.assign == approver) and (bill_state_id == 1))):
			upload_form = forms.BillAddFileForm()
	if (resume_form == None):
		resume_form = forms.ResumeForm()
	buttons = {
		'edit':		# assignee & Draft*
			(user.is_superuser or ((bill.assign == approver) and (bill_state_id == 1))),
		'del':		# assignee & (Draft|Rejected)
			(user.is_superuser or ((bill.assign == approver) and (bill_state_id in set([1, 3])) and (bill.locked == False))),
		'restart':	# assignee & (Rejected*|Done?)
			(user.is_superuser or ((bill.assign == approver) and ((bill_state_id == 3) or ((bill_state_id == 5) and (bill.locked == True))))),
		'arch':		# assignee & Done
			(user.is_superuser or (((bill.assign == approver) or user.is_staff) and (bill_state_id == 5) and (bill.locked == False))),
	}
	# Accepting (Вперед, Согласовано, В оплате, Исполнено)
	buttons['accept'] = 0
	if (bill_state_id == STATE_DRAFT):			# Draft
		if (bill.assign == approver):
			buttons['accept'] = 1		# Вперед
	elif (bill_state_id == STATE_ONWAY):		# OnWay
		if (approver.role.pk != 6):		# not Accounter
			if ((bill.rpoint.approve == None) and (bill.rpoint.role == approver.role)) or \
			   ((bill.rpoint.approve != None) and (bill.rpoint.approve == approver)):
				buttons['accept'] = 2	# Согласовано
		else:					# Accounter
			if (bill.rpoint.role == approver.role):
				buttons['accept'] = 3		# В оплате
	elif (bill_state_id == STATE_ONPAY):		# OnPay
		if (approver.role.pk == 6):		# Accounter
			buttons['accept'] = 4		# Оплачен
	# Rejecting
	buttons['reject'] = 0
	if (approver.role.pk != 6):
		if (bill_state_id == 2) and (((bill.rpoint.approve == None) and (bill.rpoint.role == approver.role)) or \
		   ((bill.rpoint.approve != None) and (bill.rpoint.approve == approver))):
			buttons['reject'] = 1
	else:
		if (bill_state_id in set([2, 4])) and (bill.rpoint.role == approver.role):
			buttons['reject'] = 1
	return render_to_response('bills/detail.html', context_instance=RequestContext(request, {
		'object': bill,
		'form': resume_form if (buttons['accept'] or buttons['reject']) else None,
		'upload_form': upload_form,
		'err': err,
		'button': buttons,
	}))

@login_required
@transaction.atomic
def	bill_delete(request, id):
	'''
	Delete bill
	ACL: root | (Assignee & (Draft|Rejected) & (not Locked))
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() in set([1, 3])) and\
	   (bill.locked == False)):
		fileseq = bill.fileseq
		bill.delete()
		fileseq.purge()
		return redirect('bill_list')
	else:
		return redirect('bills.views.bill_view', bill.pk)

@login_required
@transaction.atomic
def	bill_restart(request, id):
	'''
	Restart bill (partialy Done or Rejected)
	ACL: root | (Assignee & (Rejected | (Done & Locked)))
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   ((bill.get_state_id() == 3) or ((bill.get_state_id() == 5) and (bill.locked == True)))):
		bill.set_state_id(1)
		bill.save()
	return redirect('bills.views.bill_view', bill.pk)

@login_required
def	bill_mail(request, id):
	'''
	Test of email
	@param id: bill id
	ACL: root only
	'''
	bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser):
		utils.send_mail(
			['ti.eugene@gmail.com'],
			'Новый счет на подпись: %s' % id,
			'Вам на подпись поступил новый счет: %s' % request.build_absolute_uri(reverse('bills.views.bill_view', kwargs={'id': bill.pk})),
		)
	return redirect('bills.views.bill_view', bill.pk)

@login_required
@transaction.atomic
def	bill_toscan(request, id):
	'''
	Move bill to scans.
	ACL: root | ((Исполнитель | is_staff) && Done && !Locked)
	'''
	bill = get_object_or_404(models.Bill, pk=int(id))
	#bill = models.Bill.objects.get(pk=int(id))
	if (request.user.is_superuser) or (\
	   ((bill.assign.user.pk == request.user.pk) or request.user.is_staff) and\
	   ((bill.get_state_id() == 5) and (not bill.locked))):
		scan = Scan.objects.create(
			fileseq	= bill.fileseq,
			place	= bill.place.name,
			subject	= bill.subject.name if bill.subject else None,
			depart	= bill.depart.name if bill.depart else None,
			payer	= bill.payer.name if bill.payer else None,
			shipper	= bill.shipper,
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
		return redirect('bill_list')
	else:
		return redirect('bills.views.bill_view', bill.pk)

@login_required
def	bill_img_del(request, id):
	'''
	Delete bill img (one from).
	ACL: root | (Исполнитель && Draft)
	'''
	fsi = FileSeqItem.objects.get(pk=int(id))
	fs = fsi.fileseq
	bill = fs.bill
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() == 1)):
		fs.del_file(int(id))
	return redirect('bills.views.bill_view', fs.pk)

@login_required
#transaction.atomic
def	bill_img_up(request, id):
	'''
	Move img upper.
	ACL: root | (Исполнитель && Draft)
	'''
	fsi = FileSeqItem.objects.get(pk=int(id))
	fs = fsi.fileseq
	bill = fs.bill
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() == 1)):
		if not fsi.is_first():
			fsi.swap(fsi.order-1)
	return redirect('bills.views.bill_view', fsi.fileseq.pk)

@login_required
#transaction.atomic
def	bill_img_dn(request, id):
	'''
	Move img lower.
	ACL: root | (Исполнитель && Draft)
	'''
	fsi = FileSeqItem.objects.get(pk=int(id))
	fs = fsi.fileseq
	bill = fs.bill
	if (request.user.is_superuser) or (\
	   (bill.assign.user.pk == request.user.pk) and\
	   (bill.get_state_id() == 1)):
		if not fsi.is_last():
			fsi.swap(fsi.order+1)
	return redirect('bills.views.bill_view', fsi.fileseq.pk)
