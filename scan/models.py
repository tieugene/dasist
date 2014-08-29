# -*- coding: utf-8 -*-

# 1. django
from django.conf import settings
from django.db import models

# 2. 3rd parties

# 3. system
import os, sys, datetime, json

# 4. local
from core.models import File, FileSeq, Org

class	Scan(models.Model):
	fileseq		= models.OneToOneField(FileSeq, primary_key=True, related_name='scans', verbose_name=u'Файлы')
	place		= models.CharField(max_length=64, db_index=True, verbose_name=u'Объект')
	subject		= models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name=u'Подобъект')
	depart		= models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name=u'Направление')
	# FIXME: null=False
	payer		= models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name=u'Плательщик')
	# FIXME: null=False
	shipper		= models.ForeignKey(Org, null=True, blank=True, db_index=True, verbose_name=u'Поставщик')
	# FIXME: delete
	supplier	= models.CharField(max_length=64, db_index=True, verbose_name=u'Продавец')
	no		= models.CharField(max_length=16, db_index=True, verbose_name=u'Номер')
	date		= models.DateField(db_index=True, verbose_name=u'Дата')
	# FIXME: null=False
	sum		= models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True, db_index=True, verbose_name=u'Сумма')
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
	scan	= models.ForeignKey(Scan, db_index=True, verbose_name=u'Скан')
	approve	= models.CharField(max_length=255, db_index=True, verbose_name=u'Подписант')
	resume	= models.BooleanField(db_index=True, verbose_name=u'Резолюция')
	ctime	= models.DateTimeField(db_index=True, verbose_name=u'ДатаВремя')
	comment	= models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name=u'Камменты')

	def	__unicode__(self):
		return '%s: %s' % (self.approve, self.comment)

	class   Meta:
		ordering                = ('ctime',)
		verbose_name            = u'Резолюция'
		verbose_name_plural     = u'Резолюции'
