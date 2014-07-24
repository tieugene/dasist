# -*- coding: utf-8 -*-

# 1. django
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

# 2. 3rd parties

# 3. system
import os, sys, datetime
from StringIO import StringIO

# 4. local
#print sys.path
from core.models import File, FileSeq
#import core

STATE_ICON = (
	'document-edit.png',
	'running-man.png',
	'dialog-cancel.png',
	'dollar.png',
	'dialog-ok.png',
	'document-edit.png',
	'running-man.png',
	'dialog-cancel.png',
	'dialog-ok.png',
)

# Refs
class	State(models.Model):
	'''
	Predefined Bill states
	'''
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=16, verbose_name=u'Наименование')
	color	= models.CharField(max_length=16, verbose_name=u'Цвет')
	#icon	= models.CharField(max_length=16, blank-True, null=True, verbose_name=u'Пиктограмма')

	def	__unicode__(self):
		return self.name

	def	get_icon(self):
		return STATE_ICON[self.id-1]

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Состояние'
		verbose_name_plural     = u'Состояния'

class	Role(models.Model):
	'''
	Predefined roles
	TODO: m2m user [via Approver]
	'''
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')
	#users		= models.ManyToManyField(User, null=True, blank=True, related_name='history', through='Approver', verbose_name=u'Подписанты')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Роль'
		verbose_name_plural     = u'Роли'

class	Approver(models.Model):
	'''
	'''
	user	= models.OneToOneField(User, primary_key=True, verbose_name=u'Пользователь')
	role	= models.ForeignKey(Role, verbose_name=u'Роль')
	jobtit	= models.CharField(max_length=32, verbose_name=u'Должность')
	canadd	= models.BooleanField(verbose_name=u'Может создавать')

	class   Meta:
		ordering                = ('role', )
		verbose_name            = u'Подписант'
		verbose_name_plural     = u'Подписанты'

	def	get_fio(self):
		io = self.user.first_name.split()
		return '%s %s. %s.' % (self.user.last_name, io[0][0], io[1][0])

	def	__unicode__(self):
		return '%s %s (%s, %s)' % (self.user.last_name, self.user.first_name, self.jobtit, self.role.name)

class	Place(models.Model):
	#id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Объект'
		verbose_name_plural     = u'Объекты'

class	Subject(models.Model):
	#id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	place	= models.ForeignKey(Place, related_name='subjects', verbose_name=u'Объект')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('place', 'name',),)
		ordering                = ('place', 'id', )
		verbose_name            = u'ПодОбъект'
		verbose_name_plural     = u'ПодОбъект'

class	Department(models.Model):
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Направление'
		verbose_name_plural     = u'Направления'

class	Payer(models.Model):
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=32, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Плательщик'
		verbose_name_plural     = u'Плательщики'

# Working
class	Bill(models.Model):
	'''
	'''
	fileseq		= models.OneToOneField(FileSeq, primary_key=True, verbose_name=u'Файлы')
	place		= models.ForeignKey(Place, null=False, blank=False, verbose_name=u'Объект')
	subject		= models.ForeignKey(Subject, null=True, blank=True, verbose_name=u'ПодОбъект')
	depart		= models.ForeignKey(Department, null=True, blank=True, verbose_name=u'Направление')
	payer		= models.ForeignKey(Payer, null=True, blank=True, verbose_name=u'Плательщик')
	supplier	= models.CharField(max_length=64, verbose_name=u'Поставщик')
	billno		= models.CharField(max_length=16, verbose_name=u'Номер счета')
	billdate	= models.DateField(verbose_name=u'Дата счета')
	billsum		= models.DecimalField(max_digits=11, decimal_places=2, verbose_name=u'Сумма счета')
	payedsum	= models.DecimalField(max_digits=11, decimal_places=2, verbose_name=u'Оплачено')
	topaysum	= models.DecimalField(max_digits=11, decimal_places=2, verbose_name=u'Сумма к оплате')
	assign		= models.ForeignKey(Approver, related_name='assigned', verbose_name=u'Исполнитель')
	rpoint		= models.ForeignKey('Route', null=True, blank=True, related_name='rbill', verbose_name=u'Точка маршрута')
	#done		= models.NullBooleanField(null=True, blank=True, verbose_name=u'Закрыт')
	state		= models.ForeignKey(State, verbose_name=u'Состояние')
	#route		= SortedManyToManyField(Approver, null=True, blank=True, related_name='route', verbose_name=u'Маршрут')
	#history	= models.ManyToManyField(Approver, null=True, blank=True, related_name='history', through='BillEvent', verbose_name=u'История')

	def     __unicode__(self):
		return str(self.pk)

	#def	__get_state(self):
	#	return (self.rpoint==None, self.done)

	def	set_state_id(self, id):
		self.state = State.objects.get(pk=id)

	def	get_state_id(self):
		#return state_id[self.__get_state()]
		return self.state.pk

	def	get_state_name(self):
		#return state_name[self.__get_state()]
		return self.state.name

	def	get_state_color(self):
		#return state_color[self.__get_state()]
		return self.state.color

	class   Meta:
		#unique_together	= (('scan', 'type', 'name'),)
		#ordering		= ('id',)
		verbose_name		= u'Счет'
		verbose_name_plural	= u'Счета'

class	Route(models.Model):
	bill	= models.ForeignKey(Bill, verbose_name=u'Счет')
	order	= models.PositiveSmallIntegerField(null=False, blank=False, verbose_name=u'#')
	role	= models.ForeignKey(Role, verbose_name=u'Роль')
	approve	= models.ForeignKey(Approver, null=True, blank=True, verbose_name=u'Подписант')
	#state	= models.ForeignKey(State, verbose_name=u'Состояние')
	#action	= models.CharField(max_length=16, verbose_name=u'Действие')

	def	__unicode__(self):
		return '%d.%d: %s' % (self.bill.pk, self.order, self.approve.get_fio() if self.approve else self.role.name)

	def	get_str(self):
		#return self.approve.get_fio() if self.approve else self.role.name
		return self.approve.user.last_name if self.approve else self.role.name

	class   Meta:
		unique_together		= (('bill', 'order',),)
		ordering                = ('bill', 'order',)
		verbose_name            = u'Точка маршрута'
		verbose_name_plural     = u'Точки маршрута'

class	Event(models.Model):
	bill	= models.ForeignKey(Bill, related_name='events', verbose_name=u'Счет')
	approve	= models.ForeignKey(Approver, verbose_name=u'Подписант')
	resume	= models.BooleanField(verbose_name=u'Резолюция')
	ctime	= models.DateTimeField(auto_now_add=True, verbose_name=u'ДатаВремя')
	comment	= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Камменты')

	def	__unicode__(self):
		return '%s: %s' % (self.approve, self.comment)

	class   Meta:
		ordering                = ('ctime',)
		verbose_name            = u'Резолюция'
		verbose_name_plural     = u'Резолюции'
