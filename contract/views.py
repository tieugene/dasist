# -*- coding: utf-8 -*-
'''
contract.views
Test:
* assign: user42
* route3: user02
* route4: user03
* route1: user13
* route2: user44
* lawyer: user14
'''

# 1. system
import json
import sys

# 2. my
from bills.models import Approver, Place, State, Subject
from bills.utils import send_mail
from bills.views_extras import \
    ROLE_ACCOUNTER, ROLE_ASSIGNEE, ROLE_BOSS, ROLE_CHIEF, ROLE_LAWER, ROLE_OMTSCHIEF, \
    STATE_DONE, STATE_DRAFT, STATE_ONPAY, STATE_ONWAY, STATE_REJECTED, \
    USER_LAWER
from bills.views_extras import handle_shipper, mailto, set_filter_state

from core.models import FileSeq, FileSeqItem

# 3. django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.generic import ListView

import forms

import models

from views_extras import fill_route, update_fileseq

PAGE_SIZE = 25
FSNAME = 'contract_fstate'    # 0..4

DEFAULT_MGR = 8

reload(sys)
sys.setdefaultencoding('utf-8')


class ContractList(ListView):
    '''
    ACL:
    - All:
    -- ROLE_ASSIGNEE: только свои
    # -- ROLE_CHIEF, ROLE_ACCOUNTER - в подписантах (bold: done = False)
    -- *: все
    - Inboud:
    -- ROLE_ASSIGNEE: только свои & (Draft | Rejected)
    -- ROLE_OMTSCHIEF, ROLE_CHIEF, ROLE_BOSS, ROLE_ACCOUNTER - в подписантах & ONWAY & done = False
    -- Юрист: ONPAY

    '''
    template_name = 'contract/list.html'
    paginate_by = PAGE_SIZE
    # custom:
    # user = None
    approver = None
    mode = None

    def get_queryset(self):
        # 1. vars
        self.paginate_by = self.request.session.get('contract_lpp', PAGE_SIZE)
        user = self.request.user
        self.approver = Approver.objects.get(user=user)
        # self.approver = user.approver
        role_id = self.approver.role.pk
        if (role_id in set([ROLE_OMTSCHIEF, ROLE_BOSS, ROLE_CHIEF, ROLE_ACCOUNTER])):
            self.mode = int(self.request.session.get('contract_mode', 1))
        else:
            self.mode = 1
        # self.fsfilter = self.request.session.get(FSNAME, 63)    # int 0..15: dropped|done|onway|draft
        # 2. query
        q = models.Contract.objects.all().order_by('-pk')
        if (self.mode == 1):    # Everything
            if (user.is_superuser):
                pass
            elif (role_id == ROLE_ASSIGNEE):  # Исполнитель
                q = q.filter(assign=self.approver)
            # elif (role_id in set([ROLE_OMTSCHIEF, ROLE_BOSS, ROLE_CHIEF, ROLE_ACCOUNTER, ROLE_LAWER])):
            #    self.fsform = None
            # else:
            #    q = q.none()
            # 3. filter using Filter
            # - state
            fsfilter = self.request.session.get(FSNAME, None)
            if (fsfilter is None):
                fsfilter = 31  # all together
                self.request.session[FSNAME] = fsfilter
            else:
                fsfilter = int(fsfilter)
            q = set_filter_state(q, fsfilter)
            form_initial = {
                'dead': bool(fsfilter & 1),
                'done': bool(fsfilter & 2),
                'onpay': bool(fsfilter & 4),
                'onway': bool(fsfilter & 8),
                'draft': bool(fsfilter & 16),
            }
            # - place
            place = int(self.request.session.get('contract_place', 0))
            if (place):
                q = q.filter(place__pk=place)
                form_initial['place'] = place
            # - subject
            subject = int(self.request.session.get('contract_subject', 0))
            if (subject):
                q = q.filter(subject__pk=subject)
                form_initial['subject'] = subject
            # - depart
            depart = int(self.request.session.get('contract_depart', 0))
            if (depart):
                q = q.filter(depart__pk=depart)
                form_initial['depart'] = depart
            # - shipper
            shipper = int(self.request.session.get('contract_shipper', 0))
            if (shipper):
                q = q.filter(shipper__pk=shipper)
                form_initial['shipper'] = shipper
            # - payer
            payer = int(self.request.session.get('contract_payer', 0))
            if (payer):
                q = q.filter(payer__pk=payer)
                form_initial['payer'] = payer
            # 5. go
            self.fsform = forms.FilterContractListForm(initial=form_initial)
        else:            # Inbound
            self.fsform = None
            c_list = models.Route.objects.filter(approve=self.approver, done=False).values_list('contract_id', flat=True)
            q = q.filter(state=STATE_ONWAY, pk__in=c_list)
        return q

    def get_context_data(self, **kwargs):
        context = super(ContractList, self).get_context_data(**kwargs)
        context['lpp'] = self.paginate_by
        context['role'] = self.approver.role
        context['canadd'] = self.approver.canadd
        context['mode'] = self.mode
        context['fsform'] = self.fsform
        return context


def contract_get_subjects(request):
    '''
    AJAX callback on place change
    '''
    place = request.GET.get('place')
    ret = [dict(id='', value='---'), ]
    if place:
        for subj in Subject.objects.filter(place=place).order_by('name'):
            ret.append(dict(id=subj.pk, value=subj.name))
    return HttpResponse(json.dumps(ret), content_type='application/json')


@login_required
def contract_filter_state(request):
    '''
    Set filter on state of bill list
    POST only
    * set filter in cookie
    * redirect
    ACL: *
    '''
    fsform = forms.FilterContractListForm(request.POST)
    if fsform.is_valid():
        fsfilter = \
            int(fsform.cleaned_data['dead']) * 1 | \
            int(fsform.cleaned_data['done']) * 2 | \
            int(fsform.cleaned_data['onpay']) * 4 | \
            int(fsform.cleaned_data['onway']) * 8 | \
            int(fsform.cleaned_data['draft']) * 16
        request.session[FSNAME] = fsfilter
        request.session['contract_place'] = fsform.cleaned_data['place'].pk if fsform.cleaned_data['place'] else 0
        request.session['contract_subject'] = fsform.cleaned_data['subject'].pk if fsform.cleaned_data['subject'] else 0
        request.session['contract_depart'] = fsform.cleaned_data['depart'].pk if fsform.cleaned_data['depart'] else 0
        request.session['contract_shipper'] = fsform.cleaned_data['shipper'].pk if fsform.cleaned_data['shipper'] else 0
        request.session['contract_payer'] = fsform.cleaned_data['payer'].pk if fsform.cleaned_data['payer'] else 0
    return redirect('contract_list')


@login_required
def contract_set_lpp(request, lpp):
    '''
    Set lines-per-page of bill list.
    ACL: *
    '''
    request.session['contract_lpp'] = lpp
    return redirect('contract_list')


@login_required
def contract_set_mode(request, mode):
    '''
    Set contract list mode (all/inbound)
    ACL: *
    '''
    request.session['contract_mode'] = mode
    return redirect('contract_list')


@login_required
@transaction.atomic
def contract_add(request):
    '''
    Add new (draft) contract
    ACL: Исполнитель
    '''
    user = request.user
    approver = Approver.objects.get(user=user)
    if (approver.role.pk != ROLE_ASSIGNEE):
        return redirect('contract_list')
    if request.method == 'POST':
        form = forms.ContractAddForm(request.POST, request.FILES)
        if form.is_valid():
            # FIXME: add transaction
            # 1. create fileseq
            fileseq = FileSeq.objects.create()
            # 2. convert image and add to fileseq
            update_fileseq(request.FILES['file'], fileseq)
            # 3. bill at all
            shipper = handle_shipper(form)
            contract = models.Contract.objects.create(
                fileseq=fileseq,
                place=form.cleaned_data['place'],
                subject=form.cleaned_data['subject'],
                depart=form.cleaned_data['depart'],
                payer=form.cleaned_data['payer'],
                shipper=shipper,
                docno=form.cleaned_data['docno'],
                docdate=form.cleaned_data['docdate'],
                docsum=form.cleaned_data['docsum'],
                assign=approver,
                state=State.objects.get(pk=STATE_DRAFT),
            )
            # 4. add route
            mgr = form.cleaned_data['mgr']
            booker = form.cleaned_data['booker']
            fill_route(contract, mgr, booker)
            return redirect('contract_view', contract.pk)
    else:
        form = forms.ContractAddForm()
    return render_to_response('contract/form.html', context_instance=RequestContext(request, {
        'form': form,
        'places': Place.objects.all(),
    }))


@login_required
@transaction.atomic
def contract_edit(request, id):
    '''
    Update (edit) new Draft bill
    ACL: root | (Испольнитель & Draft)
    TODO: transaction
    '''
    contract = get_object_or_404(models.Contract, pk=int(id))    # FIXME: select_for_update(nowait=False)
    user = request.user
    approver = Approver.objects.get(pk=user.pk)
    if not (request.user.is_superuser or (
       (contract.assign == approver) and
       (contract.get_state_id() == STATE_DRAFT))):
        return redirect('contract_view', contract.pk)
    if request.method == 'POST':
        form = forms.ContractEditForm(request.POST, request.FILES)
        if form.is_valid():
            # FIXME: add transaction
            shipper = handle_shipper(form)
            # 1. update bill
            contract.place = form.cleaned_data['place']
            contract.subject = form.cleaned_data['subject']
            contract.depart = form.cleaned_data['depart']
            contract.payer = form.cleaned_data['payer']
            contract.shipper = shipper
            contract.docno = form.cleaned_data['docno']
            contract.docdate = form.cleaned_data['docdate']
            contract.docsum = form.cleaned_data['docsum']
            contract.save()    # FIXME: update()
            # 2. update mgr (if required)
            mgr = contract.get_mgr()
            if (mgr.approve != form.cleaned_data['mgr']):
                mgr.approve = form.cleaned_data['mgr']
                mgr.save()
            booker = contract.get_booker()
            if (booker.approve != form.cleaned_data['booker']):
                booker.approve = form.cleaned_data['booker']
                booker.save()
            return redirect('contract_view', contract.pk)
    else:    # GET
        form = forms.ContractEditForm(initial={
            'id':       contract.fileseq.pk,
            'place':    contract.place,
            'subject':  contract.subject,
            'depart':   contract.depart,
            'payer':    contract.payer,
            'suppinn':  contract.shipper.inn,
            'suppname': contract.shipper.name,
            'suppfull': contract.shipper.fullname,
            'docno':    contract.docno,
            'docdate':  contract.docdate,
            'docsum':   contract.docsum,
            'mgr':      contract.get_mgr().approve,    # костыль для initial
            'booker':   contract.get_booker().approve,    # костыль для initial
        })
    return render_to_response('contract/form.html', context_instance=RequestContext(request, {
        'form':     form,
        'object':   contract,
        'places':   Place.objects.all(),
    }))


@login_required
@transaction.atomic
def contract_view(request, id, upload_form=None):
    '''
    View | Accept/Reject bill
    ACL:
    - POST
    -- Исполнитель & Draft
    -- (Подписант | Роль) & Onway
    -- Юрист & OnPay
    -- Бухгалтер & Подписант.Роль [& (Onway/Onpay)]
    - POST (upload):
    -- user == Исполнитель & Draft
    - GET
    -- root
    -- Исполнитель: user == Исполнитель
    -- Руководитель: user == Подписант или в Истории
    -- *: все
    '''
    def __can_upload(contract, approver):
        '''
        ACL to uppload img.
        user == contract.approver && contract.state == Draft
        '''
        return (approver == contract.assign) and (contract.get_state_id() == STATE_DRAFT)

    def __upload(request, contract):
        '''
        Upload file to Contract
        @param request
        @parma contract:models.Contract
        @return upload_form
        '''
        upload_form = forms.ContractAddFileForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file = request.FILES.get('file', None)
            if (file):
                fileseq = contract.fileseq
                update_fileseq(file, fileseq)
        return upload_form

    def __can_approve(contract, approver):
        return contract.route_set.filter(approve=approver, done=False).count()

    def __can_resume(request, contract, approver):
        '''
        ACL to resume.
        - Draft & user == contract assign
        - OnWay & (((user in contract.route_set) & ()) | user.role == Lower)
        - OnPay==OnLawyer & user.role == Lower
        '''
        retvalue = False
        contract_state_id = contract.get_state_id()
        if (contract_state_id == STATE_DRAFT):      # Draft
            if (contract.assign == approver):
                retvalue = True
        elif (contract_state_id == STATE_ONWAY):    # OnWay
            if (approver.role.pk == ROLE_LAWER):    # Accounter
                retvalue = True
            else:
                if __can_approve(contract, approver):
                    retvalue = True
        elif (contract_state_id == STATE_ONPAY):    # OnPay == for lawyer
            if (approver.role.pk == ROLE_LAWER):    # Accounter
                retvalue = True
        return retvalue

    def __resume(request, contract):
        '''
        Resume:
        * Draft: can
        * OnWay: can
        @return resume_form, err[, redirect[ url]
        '''
        approver = models.Approver.objects.get(user=request.user)
        contract_state_id = contract.get_state_id()
        ok = False
        err = None
        resume_form = forms.ResumeForm(request.POST)
        if resume_form.is_valid():
            accepted = (request.POST['resume'] == 'accept')
            comment = resume_form.cleaned_data['note'].strip()
            # 0. check prerequisites
            if (not accepted) and (not resume_form.cleaned_data['note']):  # resume not empty on reject
                err = 'Если есть замечания - то должны быть замечания'
            else:   # as accept as reject
                if ((comment) and (accepted and contract_state_id != STATE_DRAFT)):
                    err = 'Если замечаний нет, то их и быть не должно'
                else:
                    # 1. new comment
                    contract.event_set.create(
                        approve=approver,
                        comment=comment
                    )
                    # 2. update contract
                    if (contract_state_id == STATE_DRAFT):  # Исполнитель
                        contract.set_state_id(STATE_ONWAY)
                    elif (contract_state_id == STATE_ONWAY):
                        if (__can_approve(contract, approver)):
                            route = contract.route_set.filter(approve=approver).get()
                            route.done = True
                            route.save()
                            if (contract.route_set.filter(done=False).count() == 0):
                                contract.set_state_id(STATE_ONPAY)
                            # pass    # set done = True; if everybody done state=STATE_ONPAY
                        elif ((approver.pk == USER_LAWER) and (not accepted)):
                            contract.set_state_id(STATE_REJECTED)
                            contract.route_set.filter(done=True).update(done=False)
                    elif ((contract_state_id == STATE_ONPAY) and (approver.pk == USER_LAWER)):
                            if (accepted):
                                contract.set_state_id(STATE_DONE)
                                contract.route_set.all().delete()
                            else:
                                # TODO: reset contract.route_set.all()
                                contract.route_set.filter(done=True).update(done=False)
                                contract.set_state_id(STATE_REJECTED)
                    contract.save()
                    # mailto(request, contract)
                    ok = True
        return (ok, resume_form, err)

    def __can_accept():
        pass

    def __accept():
        pass

    def __can_reject():
        pass

    def __reject():
        pass

    contract = get_object_or_404(models.Contract, pk=int(id))
    user = request.user
    approver = models.Approver.objects.get(user=user)
    contract_state_id = contract.get_state_id()
    upload_form = None
    resume_form = None
    err = ''
    if (request.method == 'POST'):
        if request.POST['action'] == 'upload':
            if (__can_upload(contract, approver)):
                upload_form = __upload(request, contract)
        else:    # resume
            if (__can_resume(request, contract, approver)):
                ok, resume_form, err = __resume(request, contract)
                if (ok):
                    return redirect('contract_list')
    else:    # GET
        if (user.is_superuser or ((contract.assign == approver) and (contract_state_id == STATE_DRAFT))):
            upload_form = forms.ContractAddFileForm()
    if (resume_form is None):   # ???
        resume_form = forms.ResumeForm()
    buttons = {
        # assignee & Draft*
        'edit': (user.is_superuser or ((contract.assign == approver) and (contract_state_id == STATE_DRAFT))),
        # assignee & (Draft|Rejected)
        'del': (user.is_superuser or ((contract.assign == approver) and (contract_state_id in set([STATE_DRAFT, STATE_REJECTED])))),
        # assignee & (Rejected*|Done?)
        'restart': (user.is_superuser or ((contract.assign == approver) and (contract_state_id == STATE_REJECTED))),
        # assignee & Done
        'arch': (user.is_superuser or (((contract.assign == approver) or user.is_staff) and (contract_state_id == STATE_DONE))),
        'accept': 0,
        'reject': 0
    }
    # Resume
    can_resume = __can_resume(request, contract, approver)
    if (can_resume):
        if (approver.role.pk == ROLE_ASSIGNEE):
            buttons['accept'] = 1   # Вперед
            buttons['reject'] = 0
        else:
            if (((approver.role.pk == ROLE_LAWER) and (contract_state_id == STATE_ONPAY)) or
                ((approver.role.pk != ROLE_LAWER) and (contract_state_id == STATE_ONWAY))):
                buttons['accept'] = 2   # Без замечаний
            buttons['reject'] = 1   # Замечание
    return render_to_response('contract/detail.html', context_instance=RequestContext(request, {
        'object': contract,
        'upload_form': upload_form,
        'form': resume_form if (buttons['accept'] or buttons['reject']) else None,
        'err': err,
        'button': buttons,
    }))


@login_required
@transaction.atomic
def contract_delete(request, id):
    '''
    Delete contract
    ACL: root | (Assignee & (Draft|Rejected))
    '''
    contract = get_object_or_404(models.Contract, pk=int(id))
    if (request.user.is_superuser) or (
       (contract.assign.user.pk == request.user.pk) and
       (contract.get_state_id() in set([STATE_DRAFT, STATE_REJECTED]))):
        fileseq = contract.fileseq
        contract.delete()
        fileseq.purge()
        return redirect('contract_list')
    else:
        return redirect('contract_view', contract.pk)


@login_required
@transaction.atomic
def contract_restart(request, id):
    '''
    Restart contract (Rejected)
    ACL: root | (Assignee & Rejected)
    '''
    contract = get_object_or_404(models.Contract, pk=int(id))
    if (request.user.is_superuser) or (
       (contract.assign.user.pk == request.user.pk) and
       (contract.get_state_id() == STATE_REJECTED)):
        contract.set_state_id(STATE_DRAFT)
        contract.save()
    return redirect('contract_view', contract.pk)


@login_required
def contract_mail(request, id):
    '''
    Test of email
    @param id: contract id
    ACL: root only
    '''
    contract = models.Contract.objects.get(pk=int(id))
    if (request.user.is_superuser):
        send_mail(
            [settings.TESTMAIL],
            'Новый договор на подпись: %s' % id,
            'Вам на подпись поступил новый договор: %s' % request.build_absolute_uri(reverse('contract_view', kwargs={'id': contract.pk})),
        )
    return redirect('contract_view', contract.pk)


@login_required
def contract_img_del(request, id):
    '''
    Delete contract img (one from).
    ACL: root | (Исполнитель && Draft)
    '''
    fsi = get_object_or_404(FileSeqItem, pk=int(id))
    fs = fsi.fileseq
    contract = fs.contract
    if (request.user.is_superuser) or (
       (contract.assign.user.pk == request.user.pk) and
       (contract.get_state_id() == STATE_DRAFT)):
        fs.del_file(int(id))
    return redirect('contract_view', fs.pk)


@login_required
# transaction.atomic
def contract_img_up(request, id):
    '''
    Move img upper.
    ACL: root | (Исполнитель && Draft)
    '''
    fsi = FileSeqItem.objects.get(pk=int(id))
    fs = fsi.fileseq
    contract = fs.contract
    if (request.user.is_superuser) or (
       (contract.assign.user.pk == request.user.pk) and
       (contract.get_state_id() == STATE_DRAFT)):
        if not fsi.is_first():
            fsi.swap(fsi.order - 1)
    return redirect('contract_view', fsi.fileseq.pk)


@login_required
# transaction.atomic
def contract_img_dn(request, id):
    '''
    Move img lower.
    ACL: root | (Исполнитель && Draft)
    '''
    fsi = FileSeqItem.objects.get(pk=int(id))
    contract = fsi.fileseq.contract
    if (request.user.is_superuser) or (
       (contract.assign.user.pk == request.user.pk) and
       (contract.get_state_id() == STATE_DRAFT)):
        if not fsi.is_last():
            fsi.swap(fsi.order + 1)
    return redirect('contract_view', fsi.fileseq.pk)
