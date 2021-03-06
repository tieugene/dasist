# -*- coding: utf-8 -*-
'''
core.views
'''

# 1. system
import json

# 2. 3rd parties
from dal import autocomplete

# 3. django
# from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView
# from django.db import transaction

# 4. my
import forms

import models

PAGE_SIZE = 25


class FileList(ListView):
    model = models.File
    template_name = 'core/file_list.html'
    paginate_by = PAGE_SIZE


class FileDetail(DetailView):
    model = models.File
    template_name = 'core/file_view.html'


class FileSeqList(ListView):
    model = models.FileSeq
    template_name = 'core/fileseq_list.html'
    paginate_by = PAGE_SIZE


class FileSeqDetail(DetailView):
    model = models.FileSeq
    template_name = 'core/fileseq_detail.html'

    def get_context_data(self, **kwargs):
        context = super(FileSeqDetail, self).get_context_data(**kwargs)
        context['form'] = forms.FileSeqItemAddForm()
        return context


@login_required
def file_preview(request, id):
    return render(request, 'core/file_img.html', {'file': models.File.objects.get(pk=int(id))})


@login_required
def file_get(request, id):
    '''
    Download file
    '''
    file = models.File.objects.get(pk=int(id))
    response = HttpResponse(content_type=file.mime)
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = '; filename=\"%s\"' % file.name.encode('utf-8')
    response.write(open(file.get_path()).read())
    return response


@login_required
def file_del(request, id):
    '''
    '''
    models.File.objects.get(pk=int(id)).delete()
    return redirect('file_list')


@login_required
def fileseq_add_file(request, id):
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
def fileseq_del(request, id):
    '''
    '''
    models.FileSeq.objects.get(pk=int(id)).delete()
    return redirect('fileseq_list')


@login_required
def fileseqitem_del(request, id):
    '''
    '''
    fsi = models.FileSeqItem.objects.get(pk=int(id))
    fs = fsi.fileseq
    fs.del_file(int(id))
    return redirect('fileseq_view', fs.pk)


@login_required
# transaction.commit_on_success
def fileseqitem_move_up(request, id):
    '''
    '''
    fsi = models.FileSeqItem.objects.get(pk=int(id))
    fs = fsi.fileseq
    order = fsi.order
    if order > 1:
        fsi.swap(fsi.order - 1)
    return redirect('fileseq_view', fs.pk)


@login_required
# transaction.commit_on_success
def fileseqitem_move_down(request, id):
    '''
    '''
    fsi = models.FileSeqItem.objects.get(pk=int(id))
    fs = fsi.fileseq
    order = fsi.order
    if fs.files.count() > order:
        fsi.swap(fsi.order + 1)
    return redirect('fileseq_view', fs.pk)


class OrgList(ListView):
    model = models.Org
    template_name = 'core/org_list.html'
    paginate_by = PAGE_SIZE


class OrgDetail(DetailView):
    model = models.Org
    template_name = 'core/org_detail.html'


def org_edit(request, id):
    org = models.Org.objects.get(pk=int(id))
    if request.method == 'POST':
        form = forms.OrgEditForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            return redirect('org_view', org.pk)
    else:
        form = forms.OrgEditForm(instance=org)
#    return render_to_response('core/org_form.html', context_instance=RequestContext(request, {
#        'form': form,
#        'object': org,
#    }))
    return render(request, 'core/org_form.html', {
        'form': form,
        'object': org,
    })


def org_get_by_inn(request):
    '''
    @param ?inn:str - INN
    @return: {'name': name, 'fullname': fullname}
    '''
    inn = request.GET.get('inn')
    org = models.Org.objects.filter(inn=inn).first()
    if org:
        ret = dict(name=org.name, fullname=org.fullname)
    else:
        ret = None
    return HttpResponse(json.dumps(ret), content_type='application/json')


class OrgAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return models.Org.objects.none()
        qs = models.Org.objects.all()
        if self.q:
            if self.q.isdigit():
                qs = qs.filter(inn__istartswith=self.q)
            else:
                qs = qs.filter(name__istartswith=self.q)
        return qs
