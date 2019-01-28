# -*- coding: utf-8 -*-
'''
contrarch.models
'''

# 3. system
import json

# 4. local
from core.models import FileSeq, Org

# 1. django
from django.db import models


class Contrarch(models.Model):
    fileseq = models.OneToOneField(FileSeq, primary_key=True, verbose_name=u'Файлы')
    place = models.CharField(max_length=24, db_index=True, verbose_name=u'Объект')
    subject = models.CharField(max_length=32, null=True, blank=True, db_index=True, verbose_name=u'Подобъект')    # max = 28
    customer = models.CharField(max_length=8, null=True, blank=True, db_index=True, verbose_name=u'Заказчик')
    depart = models.CharField(max_length=16, null=True, blank=True, db_index=True, verbose_name=u'Направление')    # max=14    # max=
    payer = models.CharField(max_length=16, db_index=True, verbose_name=u'Плательщик')
    shipper = models.ForeignKey(Org, db_index=True, verbose_name=u'Поставщик')
    docno = models.CharField(max_length=32, db_index=True, verbose_name=u'Номер')
    docdate = models.DateField(db_index=True, verbose_name=u'Дата')
    docsum = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, db_index=True, verbose_name=u'Сумма')
    # events = models.TextField(null=True, blank=True, verbose_name=u'История')

    def __unicode__(self):
        return str(self.pk)

    def decode_events(self):
        if (self.events):
            return json.loads(self.events)
        else:
            return list()

    class Meta:
        # unique_together    = (('scan', 'type', 'name'),)
        ordering = ('fileseq',)
        verbose_name = u'Договор'
        verbose_name_plural = u'Договора'


class Event(models.Model):
    contrarch = models.ForeignKey(Contrarch, db_index=True, verbose_name=u'Договор')
    ctime = models.DateTimeField(db_index=True, verbose_name=u'ДатаВремя')
    approve = models.CharField(max_length=64, db_index=True, verbose_name=u'Подписант')
    comment = models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name=u'Замечание')

    def get_approve_lname(self):
        return self.approve.split(' ', 1)[0]

    def __unicode__(self):
        return '%s: %s' % (self.approve, self.comment)

    class Meta:
        ordering = ('ctime',)
        verbose_name = u'Резолюция'
        verbose_name_plural = u'Резолюции'
