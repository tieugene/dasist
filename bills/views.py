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
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.list_detail import object_list, object_detail
from django.utils.datastructures import SortedDict
from django.db.models import F

# 2. system
import os, imp, pprint, tempfile

# 3. 3rd party

# 4. my
import models, forms

PAGE_SIZE = 20
FSNAME = 'fstate'	# 0..3

ICON = {
	'application/pdf' : 'application-pdf_32x32.png',
	'image/png': 'png_32x32.png',
	'image/tiff': 'tif_32x32.png',
}

def	__set_filter_state(q, s):
	'''
	q - original QuerySet (all)
	s - state (0..15)
	'''
	if   (s ==  0): return q.none()
	elif   (s ==  1): return q.filter(isalive = False, isgood = False)
	elif   (s ==  2): return q.filter(isalive = False, isgood = True)
	elif   (s ==  3): return q.filter(isalive = False)
	elif   (s ==  4): return q.filter(isalive = True, isgood = False)
	elif   (s ==  5): return q.filter(isgood = False)
	elif   (s ==  6): return q.exclude(isalive = F('isgood'))
	elif   (s ==  7): return q.exclude(isalive = True, isgood = True)
	elif   (s ==  8): return q.filter(isalive = True, isgood = True)
	elif   (s ==  9): return q.filter(isalive = F('isgood'))
	elif   (s == 10): return q.filter(isgood = True)
	elif   (s == 11): return q.exclude(isalive = True, isgood = False)
	elif   (s == 12): return q.filter(isalive = True)
	elif   (s == 13): return q.exclude(isalive = False, isgood = True)
	elif   (s == 14): return q.exclude(isalive = False, isgood = False)
	else: return q

@login_required
def	bill_list(request):
	'''
	List of bills
	ACL: user=assign|approve|root
	'''
	# 1. pre
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	#print approver.role.pk == 1
	queryset = models.Bill.objects.all()
	# 2. filter
	fsfilter = request.session.get(FSNAME, None)# int 0..15: dropped|done|onway|draft
	if (fsfilter == None):
		fsfilter = 15
		request.session[FSNAME] = fsfilter
	else:
		fsfilter = int(fsfilter)
	#print 'List:', fsfilter
	fsform = forms.FilterStateForm(initial={
		'dead'	:bool(fsfilter&1),
		'done'	:bool(fsfilter&2),
		'draft'	:bool(fsfilter&4),
		'onway'	:bool(fsfilter&8),
	})
	#queryset = queryset.filter(isalive=True)	# ok
	queryset = __set_filter_state(queryset, fsfilter)
	# 3. go
	#if not request.user.is_superuser:
	#	queryset = queryset.filter(assign=request.user)
	return  object_list (
		request,
		queryset = queryset,
		paginate_by = PAGE_SIZE,
		page = int(request.GET.get('page', '1')),
		template_name = 'bills/list.html',
		extra_context = {
			'canadd': approver.role.pk == 1,
			'fsform': fsform,
		}
	)

@login_required
def	bill_filter_state(request):
	'''
	POST only
	* set filter iin cookie
	* redirect
	'''
	fsform = forms.FilterStateForm(request.POST)
	if fsform.is_valid():
		fsfilter = \
			int(fsform.cleaned_data['dead']) * 1 | \
			int(fsform.cleaned_data['done']) * 2 | \
			int(fsform.cleaned_data['draft'])  * 4 | \
			int(fsform.cleaned_data['onway'])  * 8
		#print 'Filter:', fsfilter
		request.session[FSNAME] = fsfilter
	return redirect('bills.views.bill_list')

@login_required
def	bill_add(request):
	'''
	Add new (draft) bill
	ACL: root|Исполнитель
	So (transaction):
	- pre-save form
	- fill all fields
	- save bill
	- save m2m
	- save file
	'''
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	if not user.is_superuser:
		if (approver.role.pk != 1):
			return redirect('bills.views.bill_list')
	if request.method == 'POST':
		#path = request.POST['path']
		form = forms.BillForm(request.POST, request.FILES)
		if form.is_valid():
			# 1. bill at all
			bill = form.save(commit=False)
			#image = form.cleaned_data['img']
			#bill.file	= image.name
			#bill.mime	= image.content_type
			bill.assign	= approver
			bill.approve	= approver
			bill.isalive	= True
			bill.isgood	= False
			bill.save()	# FIXME: unicode error
			# 2. route
			form.save_m2m()
			# 3. file
			#with open(bill.get_path(), 'wb') as file:
			#	file.write(image.read())
			# x. the end
			return redirect('bills.views.bill_view', bill.pk)
			try:
				os.makedirs(file.get_full_dir())
				os.rename(src_path, file.get_full_path())
			except:
				transaction.rollback()
			else:
				return redirect('bills.views.bill_list')
	else:
		form = forms.BillForm()
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {'form': form,}))

@login_required
def	bill_edit(request, id):
	'''
	Update (edit) bill
	ACL: (root|assignee) & Draft
	'''
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	bill = models.Bill.objects.get(pk=int(id))
	if (not request.user.is_superuser) and (\
	   (bill.assign != approver) or\
	   (bill.get_state() != 1)):
		return redirect('bills.views.bill_view', bill.pk)
	if request.method == 'POST':
		form = forms.BillForm(request.POST, request.FILES, instance = bill)
		if form.is_valid():
			bill = form.save(commit=False)
			form.save_m2m()
			bill.save()
			#bill = form.save(commit=True)
			return redirect('bills.views.bill_view', bill.pk)
	else:
		form = forms.BillForm(instance = bill)
	return render_to_response('bills/form.html', context_instance=RequestContext(request, {
		'form': form,
		'object': bill,
	}))

@login_required
def	bill_view(request, id):
	'''
	View/Accept/Reject bill
	* create note
	* update bill:
	-- if accept:
	+-- case 1st (history len = 0 (bad) | approve == assign | user == approve | Draft):
	+--- approve = next (2nd) in route
	+--- isgood = True
	--- case last (user = route.last()):
	---- approve = assignee
	---- isalive = False
	--- case intermediate:
	---- approve = next in route
	+- if reject:
	+--- approve = assignee
	+--- isalive = False
	+--- isgood = False
	* goto list
	ACL: (assignee & Draft & Route ok) | (approver & OnWay)
	TODO:
	+ check resume not empty on reject
	+ check resume not empty on start
	- check assign can't be in route

	'''
	user = request.user
	approver = models.Approver.objects.get(pk=user.pk)
	bill = models.Bill.objects.get(pk=int(id))
	bill_state = bill.get_state()
	form = None
	err = ''
	if (request.method == 'POST'):
		if (request.POST['resume'] in set(['accept', 'reject'])) and (\
		   ((approver == bill.assign) and (bill.get_state() == 1)) or\
		   ((approver == bill.approve) and (bill.get_state() == 2)) \
		   ):
			resume = (request.POST['resume'] == 'accept')
			form = forms.ResumeForm(request.POST)
			if form.is_valid():
				# 0. check prerequisites
				if (not resume) and (not form.cleaned_data['note']):				# resume not empty on reject
					err = 'Отказ необходимо комментировать'
				elif (bill_state == 1) and (resume) and (not form.cleaned_data['note']):	# check resume not empty on start
					err = 'Запуск по маршруту необходимо комментировать'
				elif (bill_state == 1) and (resume) and (approver in bill.route.all()):	# check resume not empty on start
					err = 'Исполнитель не должен быть в маршруте'
				else:
					# 1. new comment
					models.BillEvent.objects.create(bill=bill, user=approver, comment=form.cleaned_data['note'])
					# 2. update bill
					if resume:
						route_list = bill.route.all()
						#print route_list, len(route_list), route_list[len(route_list)-1]
						routes = bill.route.count()
						print route_list
						if (bill.isgood == False):			# 1st (draft)
							#print "1st"
							bill.isgood = True
							bill.approve = route_list[0]
						elif (approver == route_list[len(route_list)-1]):		# last
							#print "Last"
							bill.approve = bill.assign
							bill.isalive = False
						else:						# intermediate
							#print "Intermediate"
							i = 0
							found = False
							for u in route_list:
								if approver == u:
									found = True
									break
								i += 1
							if (found):
								#print 'Found:', i, 'Next:', route_list[i + 1]
								bill.approve = route_list[i + 1]
					else:
						bill.approve = bill.assign
						bill.isalive = False
						bill.isgood = False
					bill.save()
					return redirect('bills.views.bill_list')
	if (form == None):
		form = forms.ResumeForm()
	return render_to_response('bills/detail.html', context_instance=RequestContext(request, {
		'object': bill,
		'icon': ICON.get(bill.mime, 'none.png'),
		'form': form,
		# root | (assignee & Draft)
		'canedit': (user.is_superuser or ((bill.assign == approver) and (bill_state == 1))),
		# root | (assignee & (Draft|Rejected)==bad)
		'candel': (user.is_superuser or ((bill.assign == approver) and (bill.isgood == False))),
		# (assignee & Draft) | (approver & OnWay)
		'canaccept': (((bill.assign == approver) and (bill_state == 1)) or ((bill.approve == approver) and (bill_state == 2))),
		# approver & OnWay
		'canreject': ((bill.approve == approver) and (bill_state == 2)),
		'pagelist': range(bill.pages),
		'err': err
	}))

@login_required
def	bill_get(request, id):
	'''
	Download bill
	ACL: any?
	'''
	bill = models.Bill.objects.get(pk=int(id))
	response = HttpResponse(mimetype=bill.mime)
	response['Content-Transfer-Encoding'] = 'binary'
	response['Content-Disposition'] = '; filename=' + bill.name.encode('utf-8')
	response.write(open(bill.get_path()).read())
	return response


@login_required
def	bill_delete(request, id):
	'''
	Delete bill
	ACL: (root|assignee) & (Draft|Rejected (bad))
	'''
	bill = models.Bill.objects.get(pk=int(id))
	if (not request.user.is_superuser) and (\
	   (bill.assign.pk != request.user.pk) or\
	   (bill.isgood == True)):
		return redirect('bills.views.bill_view', bill.pk)
	path = bill.get_path()
	if os.path.exists(path):
		os.unlink(path)
	bill.delete()
	return redirect('bills.views.bill_list')

