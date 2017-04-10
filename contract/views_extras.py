# -*- coding: utf-8 -*-
'''
contracts.views_extras
'''

# 1. system
import sys

# 2. my
from bills.models import Approver, Role
from bills.utils import send_mail
from bills.views_extras import \
    ROLE_ACCOUNTER, ROLE_BOSS, ROLE_CHIEF, ROLE_SDOCHIEF, \
    STATE_ONWAY, STATE_REJECTED, \
    USER_BOSS, USER_SDOCHIEF
from core.models import File

# 3. django
# from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

# import models

reload(sys)
sys.setdefaultencoding('utf-8')


def update_fileseq(f, fileseq):
    '''
    @param file:django.core.files.uploadedfile.InMemoryUploadedFile
    @param fileseq:FileSeq
    '''
    myfile = File(file=f)
    myfile.save()
    fileseq.add_file(myfile)


def fill_route(contract, mgr, booker):
    std_route1 = [    # role_id, approve_id
        (ROLE_SDOCHIEF, Approver.objects.get(pk=USER_SDOCHIEF)),
        (ROLE_CHIEF, mgr),
        (ROLE_BOSS, Approver.objects.get(pk=USER_BOSS)),
        (ROLE_ACCOUNTER, booker),
    ]
    for r in std_route1:
        contract.route_set.create(
            role=Role.objects.get(pk=r[0]),
            approve=r[1]
        )


def __emailto(request, emails, contract_id, subj):
    '''
    Send email to recipients
    @param emails:list - list of emails:str
    @param contract_id:int
    @param subj:str - email's Subj
    '''
    if (emails):
        send_mail(
            emails,
            '%s: %d' % (subj, contract_id),
            request.build_absolute_uri(reverse('contract.views.contract_view', kwargs={'id': contract_id})),
        )


def mailto(request, contract):
    '''
    Sends emails to people:
    - onway - to rpoint role or aprove
    - Accept/Reject - to assignee
    @param contract:Contract
    '''
    return
    if settings.MAILTO is False:
        return
    state = contract.get_state_id()
    if (state == STATE_ONWAY):
        subj = 'Договор на подпись'
        emails = list()
        for i in contract.route_set.all():
            emails.append(i.user.email)
        __emailto(request, emails, contract.pk, subj)
    elif (state == STATE_REJECTED):
        __emailto(request, [contract.assign.user.email], contract.pk, 'Договор завернут')
    # elif (state == STATE_ONPAY):
    #    __emailto(request, [.assign.user.email], contract.pk, 'Договор требует одобрения')
