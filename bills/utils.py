# -*- coding: utf-8 -*-

import email
import smtplib

from django.conf import settings
from django.shortcuts import redirect

import models


def send_mail(to, subj, body):
    if settings.MAILTO is False:
        return
    msg = email.mime.text.MIMEText(body, _charset='utf-8')
    msg['From'] = settings.EMAIL_FROM
    msg['Subject'] = subj
    # email.encoders.encode_quopri(msg)
    if (settings.DEBUG is True):
        body = ("mailto:%s\n" % to) + body
        to = settings.TESTMAIL
    server = smtplib.SMTP_SSL()
    server.connect(settings.EMAIL_HOST)    # , settings.EMAIL_PORT
    # server.ehlo()
    # if (settings.EMAIL_USE_TLS):
    #    print "3."
    #    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.sendmail(settings.EMAIL_FROM, to, msg.as_string())
    server.quit()


# def    __pdf2png1(self, src_path, thumb_template, pages):
#    for page in range(pages, 10):
#        img = Wand_Image(filename = src_path + '[%d]' % page, resolution=(150,150))
#        #print img.size
#        if (img.colorspace != 'gray'):
#            img.colorspace = 'gray'        # 'grey' as for bw as for grey (COLORSPACE_TYPES)
#        img.format = 'png'
#        #img.resolution = (300, 300)
#        img.save(filename = thumb_template % page)


def bill_toscan_json(request, id):
    '''
    '''
    bill = models.Bill.objects.get(pk=int(id))
    if (request.user.is_superuser) or (
       (bill.assign.user.pk == request.user.pk) and
       (bill.get_state_id() == 5)):
        event_list = []
        for event in (bill.events.all()):
            ev = {
                'approve':  u'%s %s (%s)' % (event.approve.user.last_name, event.approve.user.first_name, event.approve.jobtit),
                'resume':   event.resume,
                'ctime':    event.ctime.strftime('%Y-%m-%d %H:%M:%S'),
                'comment':  u'%s' % event.comment,
            }
            # print ev
            event_list.append(ev)
#        j = json.dumps(event_list, ensure_ascii=False) if event_list else ''
#         scan = Scan.objects.create(
#            fileseq=bill.fileseq,
#            place=bill.place.name,
#            subject=bill.subject.name,
#            depart=bill.depart.name,
#            payer=bill.payer.name,
#            shipper=bill.shipper,
#            no=bill.billno,
#            date=bill.billdate,
#            sum=bill.billsum,
#            events=j
#        )
        bill.delete()
        return redirect('bill_list')
    else:
        return redirect('bill_view', bill.pk)


# def send_mail_old():
#    arglist = ['mail', '-s', 'DasIst.Bills: %s: %d' % (subj, bill_id), email]
#    sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
#    stdout_data = sp.communicate(input=request.build_absolute_uri(reverse('bill_view', kwargs={'id': bill_id})))


# def send_mail_fail(request, id):
#    '''
#    @param id: bill id
#    '''
#    subj = 'DasIst.Bills: Новый счет: %s' % id
#    body = 'Новый счет на подпись: %s' % request.build_absolute_uri(reverse('bill_view', kwargs={'id': id}))
#    arglist = ['mailx', '-s', subj.encode('utf-8'), '-S' 'ttycharset=UTF-8' '-S' 'sendcharsets=UTF-8' '-S' 'encoding=8bit', 'ti.eugene@gmail.com']    # cyrillic depricated
#    sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
#    stdout_data = sp.communicate(input=body.encode('utf-8'))
#    return redirect('bill_list')


def mailto_example(request, id):
    '''
    @param id: bill id
    '''
    bill = models.Bill.objects.get(pk=int(id))
    gmail_user = 'dasist.robot@gmail.com'
    gmail_pwd = 'UktelMuctel'
    FROM = '"Согласование" <dasist.robot@gmail.com>'
    TO = ['ti.eugene@gmail.com']  # must be a list
    SUBJECT = 'Тест'
    TEXT = 'Тестовый текст'

    # Prepare actual message
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (FROM, ", ".join(TO), SUBJECT, TEXT)
    # message = 'Текст'
    try:
        # server = smtplib.SMTP(SERVER)
        server = smtplib.SMTP('smtp.gmail.com', 587)  # or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        # server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print 'failed to send mail'
    return redirect('bill_view', bill.pk)
