# -*- coding: utf-8 -*-
'''
bills.views_extras
'''

# 1. system
import os
import shutil
import subprocess
import sys
import tempfile

# 2. 3rd party
# from pyPdf import PdfFileReader
# from pdfrw import PdfReader
# from wand.image import Image as Wand_Image
from PIL import Image as PIL_Image

# 4. my
from core.models import File, Org

# 3. django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

import models

import utils

reload(sys)
sys.setdefaultencoding('utf-8')

STATE_DRAFT = 1     # Черновик
STATE_ONWAY = 2     # В пути (на подписи)
STATE_REJECTED = 3  # Завернут
STATE_ONPAY = 4     # В оплате (согласовано со всеми) (???)
STATE_DONE = 5      # Исполнен (Одобрено юристом > готово в архив)

ROLE_ASSIGNEE = 1   # Исполнитель (ОМТС) (*)
ROLE_OMTSCHIEF = 2  # Начальник ОМТС (1)
ROLE_CHIEF = 3      # Руководитель (*)
ROLE_LAWER = 4      # Юрист (1) TODO: ROLE_LAWYER
ROLE_BOSS = 5       # Гендиректор (2)
ROLE_ACCOUNTER = 6  # Бухгалтер (3)
ROLE_SDOCHIEF = 7   # Начальник СДО (1)
ROLE_GUEST = 8      # Гость (*)

# Special assigneies
USER_OMTSCHIEF = 23
USER_LAWER = 5      # => 55; TODO: USER_LAWYER
USER_BOSS = 30
USER_SDOCHIEF = 43
DEFAULT_CHIEF = 32


def set_filter_state(q, s):
    '''
    q - original QuerySet (all)
    s - state (0..31; dead|done|onpay|onway|draft)
    '''
    retvalue = q
    if (not bool(s & 1)):    # Rejected
        retvalue = retvalue.exclude(state=STATE_REJECTED)
    if (not bool(s & 2)):    # Done
        retvalue = retvalue.exclude(state=STATE_DONE)
    if (not bool(s & 4)):    # OnPay
        retvalue = retvalue.exclude(state=STATE_ONPAY)
    if (not bool(s & 8)):    # OnWay
        retvalue = retvalue.exclude(state=STATE_ONWAY)
    if (not bool(s & 16)):    # Draft
        retvalue = retvalue.exclude(state=STATE_DRAFT)
    return retvalue


def __pdf2png2(src_path, basename):
    tmpdir = tempfile.mkdtemp()
    # 1. extract
    arglist = ["gs", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pnggray", "-r150", "-sOutputFile=%s-%%d.png" % os.path.join(tmpdir, basename), src_path]
    sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.communicate()
    # 2. mv
    retvalue = os.listdir(tmpdir)
    retvalue.sort()
    for f in retvalue:
        shutil.move(os.path.join(tmpdir, f), os.path.join(settings.MEDIA_ROOT, f))
    os.rmdir(tmpdir)
    return retvalue


def __pdf2png3(src_path, basename):
    '''
    src_path - full path to src file
    basename - source file name w/o ext
    '''
    retvalue = list()
    tmpdir = tempfile.mkdtemp()
    # 1. extract
    arglist = ['pdfimages', '-q', '-j', src_path, os.path.join(tmpdir, basename)]
    sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.communicate()
    # 2. convert
    filelist = os.listdir(tmpdir)
    filelist.sort()
    for f in filelist:
        chunk_path = os.path.join(tmpdir, f)
        with open(chunk_path, 'rb') as fh:
            img = PIL_Image.open(fh)
            name, ext = f.rsplit('.', 1)
            dst_filename = name + '.png'
            # flag = {'jpg': 'L', 'ppm': 'L', 'pbm': '1'}[ext]
            img.convert('L').save(os.path.join(settings.MEDIA_ROOT, dst_filename), 'PNG')
            del img
            retvalue.append(dst_filename)
        os.unlink(chunk_path)
    os.rmdir(tmpdir)
    return retvalue


def __convert_img(file, rawpdf=False):
    '''
    Convert image
    @param file:django.core.files.uploadedfile.InMemoryUploadedFile
    @return list of output filepaths
    '''
    retvalue = list()
    # dirname = settings.MEDIA_ROOT
    filemime = file.content_type
    filename = file.name.encode('utf-8')
    src_path = os.path.join(settings.MEDIA_ROOT, filename)
    # beg
    # default_storage.save(filename, ContentFile(file.read()))    # unicode
    buffer = file.read()
    f = open(src_path, 'wb')
    f.write(buffer)
    f.close()
    # end
    basename = filename.rsplit('.', 1)[0]
    if (filemime == 'image/png'):
        img = PIL_Image.open(src_path)
        if (img.mode not in set(['1', 'L'])):    # [paletted ('P')], bw, grey
            img.convert('L').save(src_path)
        retvalue.append(filename)
    elif (filemime == 'image/jpeg'):
        img = PIL_Image.open(src_path)
        dst_filename = basename + '.png'
        img.convert('L').save(os.path.join(settings.MEDIA_ROOT, dst_filename), 'PNG')
        os.unlink(src_path)
        retvalue.append(dst_filename)
    elif (filemime == 'image/tiff'):
        img = PIL_Image.open(src_path)
        for i in range(9):
            try:
                img.seek(i)
                if (img.mode in set(['1', 'L'])):
                    thumb = img
                else:
                    thumb = img.convert('L')
                dst_filename = '%s-%d.png' % (basename, i + 1)
                thumb.save(os.path.join(settings.MEDIA_ROOT, dst_filename), 'PNG')
                retvalue.append(dst_filename)
            except EOFError:
                break
        os.unlink(src_path)
    elif (filemime == 'application/pdf'):
        if (rawpdf):
            retvalue = __pdf2png2(src_path, basename)
        else:
            retvalue = __pdf2png3(src_path, basename)
        os.unlink(src_path)
    return retvalue


def update_fileseq(f, fileseq, rawpdf=False):
    for filename in __convert_img(f, rawpdf):
        src_path = os.path.join(settings.MEDIA_ROOT, filename)
        # myfile = File(file=SimpleUploadedFile(filename, default_storage.open(filename).read()))
        myfile = File(file=SimpleUploadedFile(filename, open(src_path).read()))    # unicode error
        myfile.save()
        # default_storage.delete(filename)
        os.unlink(src_path)
        fileseq.add_file(myfile)


def handle_shipper(form):
    suppinn = form.cleaned_data['suppinn'].strip()
    shipper = Org.objects.filter(inn=suppinn).first()
    if not (shipper):    # not found > create
        shipper = Org(
            inn=suppinn,
            name=form.cleaned_data['suppname'].strip(),
            fullname=form.cleaned_data['suppfull'].strip()
        )
        shipper.save()
    return shipper


def fill_route(bill, mgr):    # , boss
    std_route1 = [    # role_id, approve_id
        (ROLE_OMTSCHIEF, models.Approver.objects.get(pk=USER_OMTSCHIEF)),   # Gorbunoff.N.V.
        (ROLE_CHIEF, mgr),                                                  # Руководитель
        (ROLE_LAWER, models.Approver.objects.get(pk=USER_LAWER)),           # Юрист
        (ROLE_BOSS, models.Approver.objects.get(pk=USER_BOSS)),             # Гендир
        (ROLE_ACCOUNTER, None),                                             # Бухгалтер
    ]
    for i, r in enumerate(std_route1):  # https://docs.djangoproject.com/en/1.10/ref/models/relations/#django.db.models.fields.related.RelatedManager.set
        bill.route_set.create(
            # bill=bill,
            order=i + 1,
            role=models.Role.objects.get(pk=r[0]),
            approve=r[1],
        )


def __emailto(request, emails, bill_id, subj):
    '''
    Send email to recipients
    @param emails:list - list of emails:str
    @param bill_id:int
    @param subj:str - email's Subj
    '''
    if (emails):
        utils.send_mail(
            emails,
            '%s: %d' % (subj, bill_id),
            request.build_absolute_uri(reverse('bills.views.bill_view', kwargs={'id': bill_id})),
        )


def mailto(request, bill):
    '''
    Sends emails to people:
    - onway - to rpoint role or aprove
    - Accept/Reject - to assignee
    @param bill:Bill
    '''
    if settings.MAILTO is False:
        return
    state = bill.get_state_id()
    if (state == STATE_ONWAY):
        subj = 'Новый счет на подпись'
        if (bill.rpoint.approve):
            emails = [bill.rpoint.approve.user.email]
        else:
            emails = list()
            for i in bill.rpoint.role.approver_set.all():
                emails.append(i.user.email)
        __emailto(request, emails, bill.pk, subj)
    elif (state == STATE_REJECTED):
        __emailto(request, [bill.assign.user.email], bill.pk, 'Счет завернут')
        # if (state == 3) and (bill.rpoint.)
    elif (state == STATE_DONE):
        if not bill.locked:
            __emailto(request, [bill.assign.user.email], bill.pk, 'Счет оплачен')
        else:
            __emailto(request, [bill.assign.user.email], bill.pk, 'Счет частично оплачен')


def rotate_img(file, dir):
    '''
    Rotate given image 90 deg right or left. Reuires ImageMagic
    @param file:core.File - file to rotate
    @param dir:bool - direction (True - right, False - left)
    '''
    arglist = ['mogrify', '-rotate', '90' if dir else '-90', file.get_path()]
    sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.communicate()
    file.update_meta()
