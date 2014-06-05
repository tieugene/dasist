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

# 4. my
import models

PAGE_SIZE = 20

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
        return  object_detail (
                request,
                queryset = models.FileSeq.objects.all(),
                object_id = id,
		template_name = 'core/fileseq_detail.html',
        )
