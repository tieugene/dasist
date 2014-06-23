# -*- coding: utf-8 -*-
'''
'''

# 1. django
#from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.db import transaction

# 4. my
import models, forms

PAGE_SIZE = 25

@login_required
def	file_list(request):
	return  object_list (
		request,
		queryset = models.File.objects.all(),
		paginate_by = PAGE_SIZE,
		page = int(request.GET.get('page', '1')),
		template_name = 'core/file_list.html',
	)

@login_required
def	file_view(request, id):
        return  object_detail (
                request,
                queryset = models.File.objects.all(),
                object_id = id,
                template_name = 'core/file_view.html',
        )

@login_required
def	file_preview(request, id):
	return render_to_response('core/file_img.html', context_instance=RequestContext(request, {'file': models.File.objects.get(pk=int(id))}))

@login_required
def	file_get(request, id):
	'''
	'''
	file = models.File.objects.get(pk=int(id))
	response = HttpResponse(mimetype=file.mime)
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
def	fileseq_list(request):
	'''
	'''
	return  object_list (
		request,
                queryset = models.FileSeq.objects.all(),
		paginate_by = PAGE_SIZE,
		page = int(request.GET.get('page', '1')),
		template_name = 'core/fileseq_list.html',
	)

@login_required
def	fileseq_view(request, id):
	'''
	'''
	if request.method == 'POST':
		form = forms.FileSeqItemAddForm(request.POST, request.FILES)
		if form.is_valid():
			if 'file' in request.FILES:
				fileseq = models.FileSeq.objects.get(pk=int(id))
				file = models.File(file=request.FILES['file'])
				file.save()
				fileseq.add_file(file)
        return  object_detail (
                request,
                queryset = models.FileSeq.objects.all(),
                object_id = id,
		template_name = 'core/fileseq_detail.html',
		extra_context = {
			'form': forms.FileSeqItemAddForm()
		}
        )

@login_required
def	fileseq_del(request, id):
	'''
	'''
	models.FileSeq.objects.get(pk=int(id)).delete()
	return redirect('core.views.fileseq_list')

@login_required
def	fileseq_add_file(request, id):
	'''
	'''
	form = forms.BillAddForm()
	return render_to_response('core/fileseq_detail.html', context_instance=RequestContext(request, {
		'form': form,
		'places': models.Place.objects.all(),
	}))

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
		new_order = fsi.order-1
		new_fsi = fs.fileseqitem_set.get(order=new_order)
		#fsi.order = 0
		new_fsi.order = order
		new_fsi.save()
		fsi.order = new_order
		fsi.save()
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
		new_order = fsi.order+1
		new_fsi = fs.fileseqitem_set.get(order=new_order)
		new_fsi.order = order
		new_fsi.save()
		fsi.order = new_order
		fsi.save()
	return redirect('core.views.fileseq_view', fs.pk)
