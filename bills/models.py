# -*- coding: utf-8 -*-
'''
bills.models
'''

# 1. local
from core.models import FileSeq, Org

# 2. django
from django.contrib.auth.models import User
from django.db import models

ORD_MGR = 2
ORD_BOSS = 4
STATE_ICON = (
    'pencil.svg',           # Edit
    'paper-plane-o.svg',    # OnWay
    'ban.svg',              # unlike
    'usd.svg',              # ?
    'check.svg',            # liked
    'archive.svg',          # put 2 archieve
)


# Refs
class State(models.Model):
    '''
    Predefined Bill states:
    1 - Черновик
    2 - В пути (на подписи у Подписантов)
    3 - Завернут (Счет: любым Подписантом; Договор: Юристом)
    4 - Оплачивается (Договор: 1. "Все дали добро, только таможня тормозит", 2. "таможня (юрист) дает добро")
    5 - Исполнен (Договор: 1. таможня дала добро; 2. Договор на базе)
    '''
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
    name = models.CharField(max_length=16, db_index=True, verbose_name=u'Наименование')
    color = models.CharField(max_length=16, db_index=True, verbose_name=u'Цвет')
    # icon    = models.CharField(max_length=16, blank-True, null=True, verbose_name=u'Пиктограмма')

    def __unicode__(self):
        return self.name

    def get_icon(self):
        return STATE_ICON[self.id - 1]

    class Meta:
        unique_together = (('name',),)
        ordering = ('id', )
        verbose_name = u'Состояние'
        verbose_name_plural = u'Состояния'


class Role(models.Model):
    '''
    Predefined roles
    TODO: m2m user [via Approver]
    '''
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
    name = models.CharField(max_length=32, db_index=True, verbose_name=u'Наименование')    # max=20
    # users        = models.ManyToManyField(User, null=True, blank=True, related_name='history', through='Approver', verbose_name=u'Подписанты')

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        ordering = ('id', )
        verbose_name = u'Роль'
        verbose_name_plural = u'Роли'


class Approver(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name=u'Пользователь')
    role = models.ForeignKey(Role, db_index=True, verbose_name=u'Роль')
    jobtit = models.CharField(max_length=32, db_index=True, verbose_name=u'Должность')    # max=28
    canadd = models.BooleanField(db_index=True, verbose_name=u'Может создавать')

    class Meta:
        ordering = ('role', )
        verbose_name = u'Подписант'
        verbose_name_plural = u'Подписанты'

    def get_fio(self):
        io = self.user.first_name.split()
        return '%s %s. %s.' % (self.user.last_name, io[0][0], io[1][0])

    def __unicode__(self):
        return '%s %s (%s, %s)' % (self.user.last_name, self.user.first_name, self.jobtit, self.role.name)


class Place(models.Model):
    name = models.CharField(max_length=24, db_index=True, verbose_name=u'Наименование')    # max=22

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        ordering = ('id', )
        verbose_name = u'Объект'
        verbose_name_plural = u'Объекты'


class Subject(models.Model):
    place = models.ForeignKey(Place, db_index=True, related_name='subjects', verbose_name=u'Объект')
    name = models.CharField(max_length=32, db_index=True, verbose_name=u'Наименование')    # max=28

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('place', 'name',),)
        ordering = ('place', 'id', )
        verbose_name = u'ПодОбъект'
        verbose_name_plural = u'ПодОбъект'


class Department(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
    name = models.CharField(max_length=16, db_index=True, verbose_name=u'Наименование')    # max=14

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        ordering = ('id', )
        verbose_name = u'Направление'
        verbose_name_plural = u'Направления'


class Payer(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
    name = models.CharField(max_length=16, db_index=True, verbose_name=u'Наименование')    # max=11

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name',),)
        ordering = ('id', )
        verbose_name = u'Плательщик'
        verbose_name_plural = u'Плательщики'


# Working
class Bill(models.Model):
    fileseq = models.OneToOneField(FileSeq, primary_key=True, verbose_name=u'Файлы')
    place = models.ForeignKey(Place, related_name='place_bills', null=False, blank=False, db_index=True, verbose_name=u'Объект')
    subject = models.ForeignKey(Subject, related_name='subject_bills', null=True, blank=True, db_index=True, verbose_name=u'ПодОбъект')
    depart = models.ForeignKey(Department, related_name='department_bills', null=True, blank=True, db_index=True, verbose_name=u'Направление')
    payer = models.ForeignKey(Payer, related_name='payer_bills', null=False, blank=False, db_index=True, verbose_name=u'Плательщик')
    shipper = models.ForeignKey(Org, related_name='shipper_bills', null=False, blank=False, db_index=True, verbose_name=u'Поставщик')
    # supplier    = models.CharField(max_length=64, null=True, blank=True, db_index=False, verbose_name=u'Продавец')    # max=38
    billno = models.CharField(max_length=32, db_index=True, verbose_name=u'Номер счета')    # max=11
    billdate = models.DateField(db_index=True, verbose_name=u'Дата счета')
    billsum = models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Сумма счета')
    payedsum = models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Оплачено')
    topaysum = models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Сумма к оплате')
    assign = models.ForeignKey(Approver, related_name='assigned_bills', db_index=True, verbose_name=u'Исполнитель')
    rpoint = models.ForeignKey('Route', null=True, blank=True, related_name='rbill', db_index=True, verbose_name=u'Точка маршрута')
    state = models.ForeignKey(State, related_name='state_bills', db_index=True, verbose_name=u'Состояние')
    locked = models.BooleanField(null=False, blank=False, default=False, db_index=True, verbose_name=u'В работе')

    def __unicode__(self):
        return str(self.pk)

    def set_state_id(self, id):
        self.state = State.objects.get(pk=id)

    def get_state_id(self):
        return self.state.pk

    def get_state_name(self):
        return self.state.name

    def get_state_color(self):
        if (self.state.pk == 5) and (self.locked):
            return 'Aquamarine'
        else:
            return self.state.color

    def get_mgr(self):
        return self.route_set.get(order=ORD_MGR)

    def get_boss(self):
        return self.route_set.get(order=ORD_BOSS)

    class Meta:
        unique_together = (('shipper', 'billno', 'billdate'),)
        verbose_name = u'Счет'
        verbose_name_plural = u'Счета'


class Route(models.Model):
    bill = models.ForeignKey(Bill, db_index=True, verbose_name=u'Счет')
    # 1-based route point (assignee excluded)
    order = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'#')
    role = models.ForeignKey(Role, db_index=True, verbose_name=u'Роль')
    approve = models.ForeignKey(Approver, null=True, blank=True, db_index=True, verbose_name=u'Подписант')

    def __unicode__(self):
        return '%d.%d: %s' % (self.bill.pk, self.order, self.approve.get_fio() if self.approve else self.role.name)

    def get_str(self):
        return self.approve.get_fio() if self.approve else self.role.name

    class Meta:
        unique_together = (('bill', 'order',), ('bill', 'role'))
        ordering = ('bill', 'order',)
        verbose_name = u'Точка маршрута'
        verbose_name_plural = u'Точки маршрута'


class Event(models.Model):
    bill = models.ForeignKey(Bill, db_index=True, verbose_name=u'Счет')
    approve = models.ForeignKey(Approver, db_index=True, verbose_name=u'Подписант')
    resume = models.BooleanField(db_index=True, verbose_name=u'Резолюция')
    ctime = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=u'ДатаВремя')
    comment = models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name=u'Камменты')  # max=107

    def __unicode__(self):
        return '%s: %s' % (self.approve, self.comment)

    class Meta:
        ordering = ('ctime',)
        verbose_name = u'Резолюция'
        verbose_name_plural = u'Резолюции'
