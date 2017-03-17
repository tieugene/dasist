# -*- coding: utf-8 -*-
'''
contracts.views_extras
'''

# 1. system
import sys

# 2. my
from bills.models import Approver, Role
from bills.views_extras import \
    ROLE_ACCOUNTER, ROLE_BOSS, ROLE_CHIEF, ROLE_OMTSCHIEF, \
    STATE_DRAFT, STATE_ONWAY, STATE_REJECTED, STATE_ONPAY, STATE_DONE, \
    USER_BOSS, USER_OMTSCHIEF
from core.models import File
from bills.utils import send_mail

# 3. django
# from django.contrib.auth.models import User

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
        (ROLE_OMTSCHIEF, Approver.objects.get(pk=USER_OMTSCHIEF)),  # Gorbunoff.N.V.
        (ROLE_CHIEF, mgr),                                          # Руководитель
        (ROLE_BOSS, Approver.objects.get(pk=USER_BOSS)),            # Гендир
        (ROLE_ACCOUNTER, booker),                                     # Бухгалтер
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
    @param bill:Bill
    '''
    return
    if settings.MAILTO is False:
        return
    state = contract.get_state_id()
    if (state == STATE_ONWAY):
        subj = 'Новый Договор на подпись'
        if (bill.rpoint.approve):
            emails = [bill.rpoint.approve.user.email]
        else:
            emails = list()
            for i in bill.rpoint.role.approver_set.all():
                emails.append(i.user.email)
        __emailto(request, emails, contract.pk, subj)
    elif (state == 3):    # Reject
        __emailto(request, [bill.assign.user.email], bill.pk, 'Счет завернут')
        # if (state == 3) and (bill.rpoint.)
    elif (state == 5):
        if not bill.locked:
            __emailto(request, [bill.assign.user.email], bill.pk, 'Счет оплачен')
        else:
            __emailto(request, [bill.assign.user.email], bill.pk, 'Счет частично оплачен')
