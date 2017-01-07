# -*- coding: utf-8 -*-

from bills.models import Approver, Role

from django.db import models


class RouteTemplate(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
    name = models.CharField(max_length=32, verbose_name=u'Наименование')
    approvers = models.ManyToManyField(Approver, null=True, blank=True, related_name='acl', through='RouteTemplateACL', verbose_name=u'Подписанты')

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('name'),)
        ordering = ('id',)
        verbose_name = u'Шаблон маршрута'
        verbose_name_plural = u'Шаблоны маршрутов'


class RouteTemplateItem(models.Model):
    tpl = models.ForeignKey(RouteTemplate, verbose_name=u'Шаблон маршрута')
    order = models.PositiveSmallIntegerField(null=False, blank=False, verbose_name=u'#')
    role = models.ForeignKey(Role, verbose_name=u'Роль')
    approve = models.ForeignKey(Approver, null=True, blank=True, verbose_name=u'Подписант')
    areq = models.BooleanField(verbose_name=u'Требует Подписанта')

    def __unicode__(self):
        return '$s #%d' % (self.tpl, self.order)

    class Meta:
        unique_together = (('tpl', 'order'),)
        ordering = ('tpl', 'order')
        verbose_name = u'Точка шаблона маршрута'
        verbose_name_plural = u'Точки шаблонов маршрутов'


class RouteTemplateACL(models.Model):
    tpl = models.ForeignKey(RouteTemplate, verbose_name=u'Шаблон маршрута')
    approve = models.ForeignKey(Approver, verbose_name=u'Подписант')

    class Meta:
        unique_together = (('tpl', 'approve'),)
        ordering = ('pk',)
        verbose_name = u'Права на маршрут'
        verbose_name_plural = u'Права на маршруты'
