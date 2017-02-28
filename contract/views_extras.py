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
    USER_BOSS, USER_OMTSCHIEF
from core.models import File

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
