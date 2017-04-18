# -*- coding: utf-8 -*-
'''
contract.models
'''

# 1. local
from bills.models import Approver, Department, Payer, Place, Role, State, Subject
from bills.views_extras import \
    ROLE_ACCOUNTER, ROLE_CHIEF

from core.models import FileSeq, Org

# 2. django
# from django.contrib.auth.models import User
from django.db import models


# Refs
class Contract(models.Model):
    fileseq = models.OneToOneField(FileSeq, primary_key=True, verbose_name=u'Файлы')
    place = models.ForeignKey(Place, related_name='place_contracts', db_index=True, verbose_name=u'Объект')
    subject = models.ForeignKey(Subject, related_name='subject_contracts', null=True, blank=True, db_index=True, verbose_name=u'ПодОбъект')
    depart = models.ForeignKey(Department, related_name='department_contracts', null=True, blank=True, db_index=True, verbose_name=u'Направление')
    payer = models.ForeignKey(Payer, related_name='payer_contracts', db_index=True, verbose_name=u'Плательщик')
    shipper = models.ForeignKey(Org, related_name='shipper_contracts', db_index=True, verbose_name=u'Поставщик')
    assign = models.ForeignKey(Approver, related_name='assigned_contracts', db_index=True, verbose_name=u'Исполнитель')
    state = models.ForeignKey(State, related_name='state_contracts', db_index=True, verbose_name=u'Состояние')
    docno = models.CharField(max_length=32, db_index=True, verbose_name=u'Номер документа')    # max=11
    docdate = models.DateField(db_index=True, verbose_name=u'Дата документа')
    docsum = models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Сумма документа')

    def __unicode__(self):
        return str(self.pk)

    def set_state_id(self, id):
        self.state = State.objects.get(pk=id)

    def get_state_id(self):
        return self.state.pk

    def get_state_name(self):
        return self.state.name

    def get_state_color(self):
        return self.state.color

    def get_mgr(self):
        return self.route_set.get(role=ROLE_CHIEF)

    def get_booker(self):
        return self.route_set.get(role=ROLE_ACCOUNTER)

    def get_is_signatory(self, approver):
        return self.route_set.get(approve=approver)

    class Meta:
        verbose_name = u'Договор'
        verbose_name_plural = u'Договора'


class Route(models.Model):
    contract = models.ForeignKey(Contract, db_index=True, verbose_name=u'Договор')
    role = models.ForeignKey(Role, related_name='+', db_index=True, verbose_name=u'Роль')
    approve = models.ForeignKey(Approver, related_name='+', db_index=True, verbose_name=u'Подписант')
    done = models.BooleanField(db_index=True, default=False, verbose_name=u'Согласовано')

    def __unicode__(self):
        return '%d: %s: %d' % (self.contract.pk, self.approve.get_fio() if self.approve else self.role.name, int(self.done))

    def get_str(self):
        return self.approve.get_fio() if self.approve else self.role.name

    class Meta:
        unique_together = (('contract', 'role'))
        ordering = ('contract',)
        verbose_name = u'Подписант'
        verbose_name_plural = u'Подписанты'


class Event(models.Model):
    contract = models.ForeignKey(Contract, db_index=True, verbose_name=u'Договор')
    ctime = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=u'ДатаВремя')
    approve = models.ForeignKey(Approver, related_name='+', db_index=True, verbose_name=u'Подписант')
    comment = models.TextField(null=True, blank=True, verbose_name=u'Камменты')

    def __unicode__(self):
        return '%s: %s' % (self.approve, self.comment)

    class Meta:
        ordering = ('ctime',)
        verbose_name = u'Резолюция'
        verbose_name_plural = u'Резолюции'
