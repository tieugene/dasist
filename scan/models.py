# -*- coding: utf-8 -*-

# 1. django
from django.conf import settings
from django.db import models

# 2. 3rd parties

# 3. system
import os, sys, datetime, json

# 4. local
from core.models import File, FileSeq

class	Scan(models.Model):
	fileseq		= models.OneToOneField(FileSeq, primary_key=True, related_name='scans', verbose_name=u'Файлы')
	place		= models.CharField(max_length=64, verbose_name=u'Объект')
	subject		= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Подобъект')
	depart		= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Направление')
	payer		= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Плательщик')
	supplier	= models.CharField(max_length=64, verbose_name=u'Поставщик')
	no		= models.CharField(max_length=16, verbose_name=u'Номер')
	date		= models.DateField(verbose_name=u'Дата')
	sum		= models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, verbose_name=u'Сумма')
	events		= models.TextField(null=True, blank=True, verbose_name=u'История')

	def	__unicode__(self):
		return str(self.pk)

	def	decode_events(self):
		if (self.events):
			return json.loads(self.events)
		else:
			return list()

	class	Meta:
		#unique_together	= (('scan', 'type', 'name'),)
		ordering		= ('fileseq',)
		verbose_name            = u'Скан'
		verbose_name_plural     = u'Сканы'

class	Event(models.Model):
	scan	= models.ForeignKey(Scan, verbose_name=u'Скан')
	approve	= models.CharField(max_length=255, verbose_name=u'Подписант')
	resume	= models.BooleanField(verbose_name=u'Резолюция')
	ctime	= models.DateTimeField(verbose_name=u'ДатаВремя')
	comment	= models.TextField(null=True, blank=True, verbose_name=u'Камменты')

	def	__unicode__(self):
		return '%s: %s' % (self.approve, self.comment)

	class   Meta:
		ordering                = ('ctime',)
		verbose_name            = u'Резолюция'
		verbose_name_plural     = u'Резолюции'
