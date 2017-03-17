# -*- coding: utf-8 -*-
'''
bills.views
'''

# 1. system
import decimal
import json
import logging
import sys

# 2. my
from core.models import FileSeq, FileSeqItem

# 3. django
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.views.generic import ListView

import forms

import models

from scan.models import Event, Scan

import utils

from views_extras import \
    DEFAULT_MGR, \
    ROLE_ACCOUNTER, ROLE_ASSIGNEE, ROLE_CHIEF, ROLE_LAWER, \
    STATE_DONE, STATE_DRAFT, STATE_ONPAY, STATE_ONWAY, STATE_REJECTED, \
    USER_BOSS
from views_extras import fill_route, handle_shipper, mailto, rotate_img, set_filter_state, update_fileseq

logger = logging.getLogger(__name__)

PAGE_SIZE = 25
FSNAME = 'fstate'    # 0..3

reload(sys)
sys.setdefaultencoding('utf-8')


class BillList(ListView):
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
    # fsfilter = None
    # place = None
    # shipper = None
    # payer = None

    def get_queryset(self):
        # 1. vars
        self.paginate_by = self.request.session.get('lpp', PAGE_SIZE)
        user = self.request.user
        self.approver = models.Approver.objects.get(user=user)
        role_id = self.approver.role.pk
        self.mode = int(self.request.session.get('mode', 1))
        # self.fsfilter = self.request.session.get(FSNAME, 31)    # int 0..15: dropped|done|onway|draft
        # 2. query
        q = models.Bill.objects.all().order_by('-pk')
        if (self.mode == 1):    # Everything
            if ((role_id == ROLE_ASSIGNEE) and (not user.is_superuser) and (not user.is_staff)):    # Исполнитель
                q = q.filter(assign=self.approver)
            # elif (user.pk == 30):        # special
            #    pass
            elif (role_id == ROLE_CHIEF):    # Руководитель
                self.fsform = None
                b_list = models.Event.objects.filter(approve=self.approver).values_list('bill_id', flat=True)
                q1 = q.filter(rpoint__approve=self.approver)
                q2 = q.filter(pk__in=b_list)
                q = q1 | q2
            # 3. filter using Filter
            # - state
            fsfilter = self.request.session.get(FSNAME, None)  # int 0..15: dropped|done|onway|draft
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
            place = int(self.request.session.get('place', 0))
            if (place):
                q = q.filter(place__pk=place)
                form_initial['place'] = place
            # - subject
            subject = int(self.request.session.get('subject', 0))
            if (subject):
                q = q.filter(subject__pk=subject)
                form_initial['subject'] = subject
            # - depart
            depart = int(self.request.session.get('depart', 0))
            if (depart):
                q = q.filter(depart__pk=depart)
                form_initial['depart'] = depart
            # - shipper
            shipper = int(self.request.session.get('shipper', 0))
            if (shipper):
                q = q.filter(shipper__pk=shipper)
                form_initial['shipper'] = shipper
            # - payer
            payer = int(self.request.session.get('payer', 0))
            if (payer):
                q = q.filter(payer__pk=payer)
                form_initial['payer'] = payer
            # 5. go
            self.fsform = forms.FilterBillListForm(initial=form_initial)
        else:            # Inbound
            self.fsform = None
            if (role_id == ROLE_ASSIGNEE):        # Исполнитель
                q = q.filter(assign=self.approver, rpoint=None)
            elif (role_id in set((ROLE_LAWER, ROLE_ACCOUNTER))):    # Юрист, Бухгалтер
                q = q.filter(rpoint__role=self.approver.role)
            else:
                q = q.filter(rpoint__approve=self.approver)
        return q

    def get_context_data(self, **kwargs):
        context = super(BillList, self).get_context_data(**kwargs)
        context['lpp'] = self.paginate_by
        context['role'] = self.approver.role
        context['canadd'] = self.approver.canadd
        context['mode'] = self.mode
        context['fsform'] = self.fsform
        return context


def bill_get_subjects(request):
    '''
    AJAX callback on place change
    '''
    place = request.GET.get('place')
    ret = [dict(id='', value='---'), ]
    if place:
        for subj in models.Subject.objects.filter(place=place).order_by('name'):
            ret.append(dict(id=subj.pk, value=subj.name))
    return HttpResponse(json.dumps(ret), content_type='application/json')


@login_required
def bill_filter_state(request):
    '''
    Set filter on state of bill list
    POST only
    * set filter in cookie
    * redirect
    ACL: *
    '''
    fsform = forms.FilterBillListForm(request.POST)
    if fsform.is_valid():
        fsfilter = \
            int(fsform.cleaned_data['dead']) * 1 | \
            int(fsform.cleaned_data['done']) * 2 | \
            int(fsform.cleaned_data['onpay']) * 4 | \
            int(fsform.cleaned_data['onway']) * 8 | \
            int(fsform.cleaned_data['draft']) * 16
        request.session[FSNAME] = fsfilter
        request.session['place'] = fsform.cleaned_data['place'].pk if fsform.cleaned_data['place'] else 0
        request.session['subject'] = fsform.cleaned_data['subject'].pk if fsform.cleaned_data['subject'] else 0
        request.session['depart'] = fsform.cleaned_data['depart'].pk if fsform.cleaned_data['depart'] else 0
        request.session['shipper'] = fsform.cleaned_data['shipper'].pk if fsform.cleaned_data['shipper'] else 0
        request.session['payer'] = fsform.cleaned_data['payer'].pk if fsform.cleaned_data['payer'] else 0
    return redirect('bill_list')


@login_required
def bill_set_lpp(request, lpp):
    '''
    Set lines-per-page of bill list.
    ACL: *
    '''
    request.session['lpp'] = lpp
    return redirect('bill_list')


@login_required
def bill_set_mode(request, mode):
    '''
    Set bill list mode (all/inbound)
    ACL: *
    '''
    request.session['mode'] = mode
    return redirect('bill_list')


@login_required
@transaction.atomic
def bill_add(request):
    '''
    Add new (draft) bill
    ACL: Исполнитель
    '''
    user = request.user
    approver = models.Approver.objects.get(user=user)
    if (approver.role.pk != ROLE_ASSIGNEE):
        return redirect('bill_list')
    if request.method == 'POST':
        # path = request.POST['path']
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
                fileseq=fileseq,
                place=form.cleaned_data['place'],
                subject=form.cleaned_data['subject'],
                depart=form.cleaned_data['depart'],
                payer=form.cleaned_data['payer'],
                shipper=shipper,
                billno=form.cleaned_data['billno'],
                billdate=form.cleaned_data['billdate'],
                billsum=form.cleaned_data['billsum'],
                payedsum=form.cleaned_data['payedsum'],
                topaysum=form.cleaned_data['topaysum'],
                assign=approver,
                rpoint=None,
                state=models.State.objects.get(pk=STATE_DRAFT),
            )
            # 4. add route
            mgr = form.cleaned_data['mgr']
            # boss = form.cleaned_data['boss']
            fill_route(bill, mgr)   # , boss
            return redirect('bill_view', bill.pk)
    else:
        form = forms.BillAddForm()
    return render_to_response('bills/form.html', context_instance=RequestContext(request, {
        'form': form,
        'places': models.Place.objects.all(),
    }))


@login_required
@transaction.atomic
def bill_edit(request, id):
    '''
    Update (edit) new Draft bill
    ACL: root | (Испольнитель & Draft & !Locked)
    TODO: transaction
    '''
    bill = get_object_or_404(models.Bill, pk=int(id))    # FIXME: select_for_update(nowait=False)
    # bill = models.Bill.objects.get(pk=int(id))
    user = request.user
    approver = models.Approver.objects.get(pk=user.pk)
    if not (request.user.is_superuser or (
       (bill.assign == approver) and
       (bill.get_state_id() == STATE_DRAFT) and
       (not bill.locked))):
        return redirect('bills.views.bill_view', bill.pk)
    if request.method == 'POST':
        form = forms.BillEditForm(request.POST, request.FILES)
        if form.is_valid():
            # FIXME: add transaction
            shipper = handle_shipper(form)
            # 1. update bill
            bill.place = form.cleaned_data['place']
            bill.subject = form.cleaned_data['subject']
            bill.depart = form.cleaned_data['depart']
            bill.payer = form.cleaned_data['payer']
            bill.shipper = shipper
            bill.billno = form.cleaned_data['billno']
            bill.billdate = form.cleaned_data['billdate']
            bill.billsum = form.cleaned_data['billsum']
            bill.payedsum = form.cleaned_data['payedsum']
            bill.topaysum = form.cleaned_data['topaysum']
            bill.save()    # FIXME: update()
            # 2. update mgr (if required)
            mgr = bill.get_mgr()
            if (mgr.approve != form.cleaned_data['mgr']):
                mgr.approve = form.cleaned_data['mgr']
                mgr.save()
            # 2. update boss (if required)
            boss = bill.get_boss()
            # if (boss.approve != form.cleaned_data['boss']):
            #     boss.approve = form.cleaned_data['boss']
            if (boss.approve.pk != USER_BOSS):
                boss.approve = models.Approver.objects.get(pk=USER_BOSS)
                boss.save()
            # 3. update image
            file = request.FILES.get('file', None)
            if (file):
                fileseq = bill.fileseq
                fileseq.clean_children()
                update_fileseq(file, fileseq, form.cleaned_data['rawpdf'])    # unicode error
            return redirect('bills.views.bill_view', bill.pk)
    else:    # GET
        form = forms.BillEditForm(initial={
            'id':       bill.fileseq.pk,
            'place':    bill.place,
            'subject':  bill.subject,
            'depart':   bill.depart,
            'payer':    bill.payer,
            'suppinn':  bill.shipper.inn,
            'suppname': bill.shipper.name,
            'suppfull': bill.shipper.fullname,
            'billno':   bill.billno,
            'billdate': bill.billdate,
            'billsum':  bill.billsum,
            'payedsum': bill.payedsum,
            'topaysum': bill.topaysum,
            'mgr':      bill.get_mgr().approve,    # костыль для initial
            # 'boss':     bill.get_boss().approve,    # костыль для initial
            # 'approver':    6,
        })
    return render_to_response('bills/form.html', context_instance=RequestContext(request, {
        'form':     form,
        'object':   bill,
        'places':   models.Place.objects.all(),
    }))


@login_required
@transaction.atomic
def bill_reedit(request, id):
    '''
    Update (edit) locked Draft bill
    ACL: root | (Испольнитель & Draft & Locked)
    '''
    bill = get_object_or_404(models.Bill, pk=int(id))
    # bill = models.Bill.objects.get(pk=int(id))
    user = request.user
    approver = models.Approver.objects.get(pk=user.pk)
    if not (request.user.is_superuser or (
       (bill.assign == approver) and
       (bill.get_state_id() == STATE_DRAFT) and
       (bill.locked))):
        return redirect('bill_view', bill.pk)
    max_topaysum = bill.billsum - bill.payedsum
    if request.method == 'POST':
        form = forms.BillReEditForm(request.POST, max_topaysum=bill.billsum - bill.payedsum)
        if form.is_valid():
            # 1. update bill
            bill.topaysum = form.cleaned_data['topaysum']
            bill.save()
            # 2. update mgr (if required)
            mgr = bill.get_mgr()
            if (mgr.approve != form.cleaned_data['mgr']):
                mgr.approve = form.cleaned_data['mgr']
                mgr.save()
            # 2. and boss (if required)
            boss = bill.get_boss()
            # if (boss.approve != form.cleaned_data['boss']):
            #    boss.approve = form.cleaned_data['boss']
            if (boss.approve.pk != USER_BOSS):
                boss.approve = models.Approver.objects.get(pk=USER_BOSS)
                boss.save()
            return redirect('bill_view', bill.pk)
    else:    # GET
        # hack
        if (bill.route_set.count() == 0):
            mgr = models.Approver.objects.get(pk=DEFAULT_MGR)
            # boss = models.Approver.objects.get(pk=DEFAULT_BOSS)
            fill_route(bill, mgr)   # , boss
        # /hack
        form = forms.BillReEditForm(initial={
            'topaysum': bill.topaysum if bill.topaysum else max_topaysum,
            'mgr':      bill.get_mgr().approve,
            # 'boss':     bill.get_boss().approve,
        })
    return render_to_response('bills/form_reedit.html', context_instance=RequestContext(request, {
        'form': form,
        'object': bill,
    }))


@login_required
@transaction.atomic
def bill_view(request, id, upload_form=None):
    '''
    TODO: use __can_resume()
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
    def __can_upload(bill, approver):
        '''
        ACL to uppload img.
        user == bill.approver && bill.state == Draft
        '''
        return (approver == bill.assign) and (bill.get_state_id() == STATE_DRAFT)

    def __upload(request, bill):
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
                update_fileseq(file, fileseq, upload_form.cleaned_data['rawpdf'])    # unicode error
        return upload_form

    def __can_resume(request, bill, approver):
        '''
        ACL to resume.
        - Draft and user == bill assign
        - OnWay and ((user == bill.rpoint.user) or (user.role == bill.rpoint.role))
        - OnPay and user.role == Accounter
        '''
        bill_state_id = bill.get_state_id()
        return (
          (request.POST['resume'] in set(['accept', 'reject'])) and
          (
            ((bill_state_id == STATE_DRAFT) and (approver == bill.assign)) or
            (
              (bill_state_id == STATE_ONWAY) and (
                ((bill.rpoint.approve is not None) and (approver == bill.rpoint.approve)) or
                ((bill.rpoint.approve is None) and (approver.role == bill.rpoint.role))
              )
            ) or
            ((bill_state_id == STATE_ONPAY) and (approver.role == bill.rpoint.role))
          )
        )

    def __resume(request, bill):
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
            if (not resume) and (not resume_form.cleaned_data['note']):            # resume not empty on reject
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
                if resume:    # Ok
                    route_list = bill.route_set.all().order_by('order')
                    if (bill_state_id == STATE_DRAFT):    # 1. 1st (draft)
                        bill.rpoint = route_list[0]
                        bill.set_state_id(STATE_ONWAY)
                    elif (bill_state_id == STATE_ONWAY):    # 2. onway
                        rpoint = bill.rpoint
                        if (rpoint.order == len(route_list)):    # 2. last (accounter)
                            bill.set_state_id(STATE_ONPAY)
                        else:                    # 3. intermediate
                            bill.rpoint = bill.route_set.get(order=rpoint.order + 1)
                    elif (bill_state_id == STATE_ONPAY):    # OnPay
                        bill.rpoint = None
                        bill.payedsum += bill.topaysum
                        bill.topaysum = decimal.Decimal('0.00')
                        bill.set_state_id(STATE_DONE)
                        bill.locked = (bill.payedsum < bill.billsum)
                else:        # Reject
                    bill.set_state_id(STATE_REJECTED)
                    bill.rpoint = None
                bill.save()
                if (bill.get_state_id() == STATE_DONE) and (bill.locked is False):    # That's all
                    bill.route_set.all().delete()
                mailto(request, bill)
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
        else:    # resume
            if (__can_resume(request, bill, approver)):
                ok, resume_form, err = __resume(request, bill)
                if (ok):
                    return redirect('bill_list')
    else:    # GET
        if (user.is_superuser or ((bill.assign == approver) and (bill_state_id == STATE_DRAFT))):
            upload_form = forms.BillAddFileForm()
    if (resume_form is None):
        resume_form = forms.ResumeForm()
    buttons = {
        # assignee & Draft*
        'edit': (user.is_superuser or ((bill.assign == approver) and (bill_state_id == STATE_DRAFT))),
        # assignee & (Draft|Rejected)
        'del': (user.is_superuser or ((bill.assign == approver) and (bill_state_id in set([STATE_DRAFT, STATE_REJECTED])) and (bill.locked is False))),
        # assignee & (Rejected*|Done?)
        'restart': (user.is_superuser or ((bill.assign == approver) and ((bill_state_id == STATE_REJECTED) or ((bill_state_id == STATE_DONE) and (bill.locked is True))))),
        # assignee & Done
        'arch': (user.is_superuser or (((bill.assign == approver) or user.is_staff) and (bill_state_id == STATE_DONE) and (bill.locked is False))),
    }
    # Accepting (Вперед, Согласовано, В оплате, Исполнено)
    buttons['accept'] = 0
    if (bill_state_id == STATE_DRAFT):            # Draft
        if (bill.assign == approver):
            buttons['accept'] = 1        # Вперед
    elif (bill_state_id == STATE_ONWAY):        # OnWay
        if (approver.role.pk != 6):        # not Accounter
            if (((bill.rpoint.approve is None) and (bill.rpoint.role == approver.role)) or
               ((bill.rpoint.approve is not None) and (bill.rpoint.approve == approver))):
                buttons['accept'] = 2    # Согласовано
        else:                    # Accounter
            if (bill.rpoint.role == approver.role):
                buttons['accept'] = 3        # В оплате
    elif (bill_state_id == STATE_ONPAY):        # OnPay
        if (approver.role.pk == ROLE_ACCOUNTER):        # Accounter
            buttons['accept'] = 4        # Оплачен
    # Rejecting
    buttons['reject'] = 0
    if (approver.role.pk != ROLE_ACCOUNTER):
        if (bill_state_id == STATE_ONWAY) and (((bill.rpoint.approve is None) and (bill.rpoint.role == approver.role)) or
           ((bill.rpoint.approve is not None) and (bill.rpoint.approve == approver))):
            buttons['reject'] = 1
    else:
        if (bill_state_id in set([STATE_ONWAY, STATE_ONPAY])) and (bill.rpoint.role == approver.role):
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
def bill_delete(request, id):
    '''
    Delete bill
    ACL: root | (Assignee & (Draft|Rejected) & (not Locked))
    '''
    bill = get_object_or_404(models.Bill, pk=int(id))
    # bill = models.Bill.objects.get(pk=int(id))
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       (bill.get_state_id() in set([STATE_DRAFT, STATE_REJECTED])) and
       (bill.locked is False)):
        fileseq = bill.fileseq
        bill.delete()
        fileseq.purge()
        return redirect('bill_list')
    else:
        return redirect('bill_view', bill.pk)


@login_required
@transaction.atomic
def bill_restart(request, id):
    '''
    Restart bill (partialy Done or Rejected)
    ACL: root | (Assignee & (Rejected | (Done & Locked)))
    '''
    bill = get_object_or_404(models.Bill, pk=int(id))
    # bill = models.Bill.objects.get(pk=int(id))
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       ((bill.get_state_id() == STATE_REJECTED) or ((bill.get_state_id() == STATE_DONE) and (bill.locked is True)))):
        bill.set_state_id(STATE_DRAFT)
        bill.save()
    return redirect('bill_view', bill.pk)


@login_required
def bill_mail(request, id):
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
    return redirect('bill_view', bill.pk)


@login_required
@transaction.atomic
def bill_toscan(request, id):
    '''
    Move bill to scans.
    ACL: root | ((Исполнитель | is_staff) && Done && !Locked)
    '''
    bill = get_object_or_404(models.Bill, pk=int(id))
    # bill = models.Bill.objects.get(pk=int(id))
    if (request.user.is_superuser) or (
       ((bill.assign.user.pk == request.user.pk) or request.user.is_staff) and
       ((bill.get_state_id() == STATE_DONE) and (not bill.locked))):
        scan = Scan.objects.create(
            fileseq=bill.fileseq,
            place=bill.place.name,
            subject=bill.subject.name if bill.subject else None,
            depart=bill.depart.name if bill.depart else None,
            payer=bill.payer.name if bill.payer else None,
            shipper=bill.shipper,
            supplier=bill.shipper.name,
            no=bill.billno,
            date=bill.billdate,
            sum=bill.billsum,
        )
        # for event in (bill.events.all()):
        for event in (bill.event_set.all()):
            scan.event_set.create(
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
def bill_img_del(request, id):
    '''
    Delete bill img (one from).
    ACL: root | (Исполнитель && Draft)
    '''
    fsi = get_object_or_404(FileSeqItem, pk=int(id))
    fs = fsi.fileseq
    bill = fs.bill
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       (bill.get_state_id() == STATE_DRAFT)):
        fs.del_file(int(id))
    return redirect('bills.views.bill_view', fs.pk)


@login_required
# transaction.atomic
def bill_img_up(request, id):
    '''
    Move img upper.
    ACL: root | (Исполнитель && Draft)
    '''
    fsi = FileSeqItem.objects.get(pk=int(id))
    fs = fsi.fileseq
    bill = fs.bill
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       (bill.get_state_id() == STATE_DRAFT)):
        if not fsi.is_first():
            fsi.swap(fsi.order - 1)
    return redirect('bills.views.bill_view', fsi.fileseq.pk)


@login_required
# transaction.atomic
def bill_img_dn(request, id):
    '''
    Move img lower.
    ACL: root | (Исполнитель && Draft)
    '''
    fsi = FileSeqItem.objects.get(pk=int(id))
    bill = fsi.fileseq.bill
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       (bill.get_state_id() == STATE_DRAFT)):
        if not fsi.is_last():
            fsi.swap(fsi.order + 1)
    return redirect('bills.views.bill_view', fsi.fileseq.pk)


def __bill_img_r(request, id, dir):
    '''
    Rotate image
    '''
    fsi = FileSeqItem.objects.get(pk=int(id))
    bill = fsi.fileseq.bill
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       (bill.get_state_id() == STATE_DRAFT)):
        rotate_img(fsi.file, dir)
    return redirect('bills.views.bill_view', fsi.fileseq.pk)


@login_required
def bill_img_rl(request, id):
    '''
    Rotate img left
    '''
    return __bill_img_r(request, id, False)


@login_required
def bill_img_rr(request, id):
    '''
    Rotate img right
    '''
    return __bill_img_r(request, id, True)
