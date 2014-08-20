# -*- coding: utf-8 -*-
'''
core.views
'''

# 1. django
#from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.db import transaction

# 2. system
import simplejson

# 4. my
import models, forms

PAGE_SIZE = 25

class	FileList(ListView):
	model = models.File
	template_name = 'core/file_list.html'
	paginate_by = PAGE_SIZE

class	FileDetail(DetailView):
	model = models.File
	template_name = 'core/file_view.html'

class	FileSeqList(ListView):
	model = models.FileSeq
	template_name = 'core/fileseq_list.html'
	paginate_by = PAGE_SIZE

class	FileSeqDetail(DetailView):
	model = models.FileSeq
	template_name = 'core/fileseq_detail.html'

	def	get_context_data(self, **kwargs):
		context = super(FileSeqDetail, self).get_context_data(**kwargs)
		context['form']	= forms.FileSeqItemAddForm()
		return context

@login_required
def	file_preview(request, id):
	return render_to_response('core/file_img.html', context_instance=RequestContext(request, {'file': models.File.objects.get(pk=int(id))}))

@login_required
def	file_get(request, id):
	'''
	'''
	file = models.File.objects.get(pk=int(id))
	response = HttpResponse(content_type=file.mime)
	response['Content-Transfer-Encoding'] = 'binary'
	response['Content-Disposition'] = '; filename=\"%s\"' % file.name.encode('utf-8')
	response.write(open(file.get_path()).read())
	return response

@login_required
def	file_del(request, id):
	'''
	'''
	models.File.objects.get(pk=int(id)).delete()
	return redirect('core.views.file_list')

@login_required
def	fileseq_add_file(request, id):
	'''
	'''
	form = forms.FileSeqItemAddForm(request.POST, request.FILES)
	if form.is_valid():
		if 'file' in request.FILES:
			fileseq = models.FileSeq.objects.get(pk=int(id))
			file = models.File(file=request.FILES['file'])
			file.save()
			fileseq.add_file(file)
	return redirect('fileseq_view', id)

@login_required
def	fileseq_del(request, id):
	'''
	'''
	models.FileSeq.objects.get(pk=int(id)).delete()
	return redirect('fileseq_list')

@login_required
def	fileseqitem_del(request, id):
	'''
	'''
	fsi = models.FileSeqItem.objects.get(pk=int(id))
	fs = fsi.fileseq
	fs.del_file(int(id))
	return redirect('core.views.fileseq_view', fs.pk)

@login_required
@transaction.commit_on_success
def	fileseqitem_move_up(request, id):
	'''
	'''
	fsi = models.FileSeqItem.objects.get(pk=int(id))
	fs = fsi.fileseq
	order = fsi.order
	if order > 1:
		fsi.swap(fsi.order-1)
	return redirect('core.views.fileseq_view', fs.pk)

@login_required
@transaction.commit_on_success
def	fileseqitem_move_down(request, id):
	'''
	'''
	fsi = models.FileSeqItem.objects.get(pk=int(id))
	fs = fsi.fileseq
	order = fsi.order
	if fs.files.count() > order:
		fsi.swap(fsi.order+1)
	return redirect('core.views.fileseq_view', fs.pk)

class	OrgList(ListView):
	model = models.Org
	template_name = 'core/org_list.html'
	paginate_by = PAGE_SIZE

class	OrgDetail(DetailView):
	model = models.Org
	template_name = 'core/org_detail.html'

def	org_get_by_inn(request):
	'''
	@param ?inn:str - INN
	@return: {'name': name, 'fullname': fullname}
	'''
	inn=request.GET.get('inn')
	org = models.Org.objects.filter(inn=inn).first()
	if org:
		ret = dict(name = org.name, fullname = org.fullname)
	else:
		ret = None
	return HttpResponse(simplejson.dumps(ret), content_type='application/json')
