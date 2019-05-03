# -*- coding: utf-8 -*-
'''
urls
dasist 0.?.?
'''

import os

import bills

import contract

import contrarch

import core

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

import scan


# import pprint


def common_context(context):
    '''
    our context processor. Add to dict vars to send in ALL templates.
    '''
    return {
        'LOGIN_URL':    settings.LOGIN_URL,
        'path':         'apps.core'
    }


def __get_bs():
    return frozenset(bills.models.Bill.objects.values_list('pk', flat=True).order_by('pk'))


def __get_sc():
    return frozenset(scan.models.Scan.objects.values_list('pk', flat=True).order_by('pk'))


def __get_ct():
    return frozenset(contract.models.Contract.objects.values_list('pk', flat=True).order_by('pk'))


def __get_ca():
    return frozenset(contrarch.models.Contrarch.objects.values_list('pk', flat=True).order_by('pk'))


def __get_fs():
    return frozenset(core.models.FileSeq.objects.values_list('pk', flat=True).order_by('pk'))


def __get_fsi_f():
    return frozenset(core.models.FileSeqItem.objects.values_list('file', flat=True).order_by('file'))


def __get_fsi_fs():
    return frozenset(core.models.FileSeqItem.objects.values_list('fileseq', flat=True).order_by('fileseq'))


def __get_ff():
    return frozenset(core.models.File.objects.values_list('pk', flat=True).order_by('pk'))


def __get_fh():
    fh = set()  # files hw
    for i in os.listdir(settings.MEDIA_ROOT):
        if i.isdigit():
            fh.add(int(i))
    fh = frozenset(fh)
    return fh


@login_required
# @transaction.atomic
def chk(request):
    '''
    Chk orphaned/widows:
    1. X Bill/Scan/Contract/Contrarch
    2. orphaned FileSeq (w/o Bill|Scan|Contract|ContrArch)
    3. empty FileSeq (w/o FileSeqItem)
    4. orphaned File (w/o FileSeqItem)
    5. empty File (w/o file)
    6. orphaned files (w/o File)

    Set:
    X - +, /, *, %
    - - (вычитание: есть в A, но нет в B)
    & - (пересечение: есть в A и в B)
    | - a | b (объединение: есть в A или в B)
    ^ - исключение (есть в A или в B, но не в обоих одновременно)
    '''
    # 0.
    bs = __get_bs()
    sc = __get_sc()
    ct = __get_ct()
    ca = __get_ca()
    fs = __get_fs()
    ff = __get_ff()
    fsi_f = __get_fsi_f()
    fsi_fs = __get_fsi_fs()
    fh = __get_fh()
    return render(request, 'chk.html', {
        'bssc':     bs & sc,                            # Bill x Scan
        'bsct':     bs & ct,                            # Bill x Contract
        'bsca':     bs & ca,                            # Bill x ContrArch
        'scct':     sc & ct,                            # Scan x Contract
        'scca':     sc & ca,                            # Scan x ContrArch
        'ctca':     ct & ca,                            # Contract x ContrArch
        'fs_orph':  sorted(fs - (bs | sc | ct | ca)),   # 2.
        'fs_wo_fsi': sorted(fs - fsi_fs),               # 3.
        'ff_wo_fsi': sorted(ff - fsi_f),                # 4.
        'ff_wo_fh':  sorted(ff - fh),                   # 5.
        'fh_wo_ff':  sorted(fh - ff),                   # 6.
    })


def cln(request, f):
    '''
    f - function no
    '''
    f = int(f)
    # pre
    bs = __get_bs()
    sc = __get_sc()
    ct = __get_ct()
    ca = __get_ca()
    fs = __get_fs()
    ff = __get_ff()
    fsi_f = __get_fsi_f()
    fsi_fs = __get_fsi_fs()
    fh = __get_fh()
    # post
    if (f == 1):    # 1. X
        pass
    elif (f == 2):  # 2. orphaned FileSeq (OK)
        q = fs - (bs | sc | ct | ca)
        core.models.FileSeq.objects.filter(pk__in=q).delete()
    elif (f == 3):  # 3. empty FileSeq (OK)
        q = fs - fsi_fs
        core.models.FileSeq.objects.filter(pk__in=q).delete()
    elif (f == 4):  # 4. orphaned File (OK)
        q = ff - fsi_f
        core.models.File.objects.filter(pk__in=q).delete()
    elif (f == 5):  # 5. empty File
        q = ff - fh
        core.models.File.objects.filter(pk__in=q).delete()
    elif (f == 6):  # 6. orphaned file (OK)
        # f  = __get_f()
        for i in (fh - ff):
            full_fh = os.path.join(settings.MEDIA_ROOT, '%08d' % i)
            if (os.path.exists(full_fh)):
                os.unlink(full_fh)
    else:
        pass
    return redirect('chk')
