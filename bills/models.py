# -*- coding: utf-8 -*-
'''
bills.models
'''

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
from core.models import File, FileSeq, Org
#import core

from views_extras import ROLE_CHIEF, ROLE_BOSS

ORD_MGR		= 2
ORD_BOSS	= 4

STATE_ICON = (
	'pencil.svg',
	'paper-plane-o.svg',
	'ban.svg',
	'usd.svg',
	'check.svg',
	'archive.svg',
)

# Refs
class	State(models.Model):
	'''
	Predefined Bill states
	'''
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=16, db_index=True, verbose_name=u'Наименование')
	color	= models.CharField(max_length=16, db_index=True, verbose_name=u'Цвет')
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
	name	= models.CharField(max_length=32, db_index=True, verbose_name=u'Наименование')	# max=20
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
	"Foreign key constraint is incorrectly formed"
	Refers to non-existant table User?
	class Approver(User) not helps
	'''
	user	= models.OneToOneField(User, primary_key=True, verbose_name=u'Пользователь')	# FAIL!
	role	= models.ForeignKey(Role, db_index=True, verbose_name=u'Роль')
	jobtit	= models.CharField(max_length=32, db_index=True, verbose_name=u'Должность')	# max=28
	canadd	= models.BooleanField(db_index=True, verbose_name=u'Может создавать')

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
	name	= models.CharField(max_length=24, db_index=True, verbose_name=u'Наименование')	# max=22

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Объект'
		verbose_name_plural     = u'Объекты'

class	Subject(models.Model):
	place	= models.ForeignKey(Place, db_index=True, related_name='subjects', verbose_name=u'Объект')
	name	= models.CharField(max_length=32, db_index=True, verbose_name=u'Наименование')	# max=28

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('place', 'name',),)
		ordering                = ('place', 'id', )
		verbose_name            = u'ПодОбъект'
		verbose_name_plural     = u'ПодОбъект'

class	Department(models.Model):
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=16, db_index=True, verbose_name=u'Наименование')	# max=14

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Направление'
		verbose_name_plural     = u'Направления'

class	Payer(models.Model):
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=16, db_index=True, verbose_name=u'Наименование')	# max=11

	def	__unicode__(self):
		return self.name

	class   Meta:
		unique_together		= (('name',),)
		ordering                = ('id', )
		verbose_name            = u'Плательщик'
		verbose_name_plural     = u'Плательщики'

# Working

class	Bill(models.Model):
	fileseq		= models.OneToOneField(FileSeq, primary_key=True, verbose_name=u'Файлы')
	place		= models.ForeignKey(Place, null=False, blank=False, db_index=True, verbose_name=u'Объект')
	subject		= models.ForeignKey(Subject, null=True, blank=True, db_index=True, verbose_name=u'ПодОбъект')
	depart		= models.ForeignKey(Department, null=True, blank=True, db_index=True, verbose_name=u'Направление')
	payer		= models.ForeignKey(Payer, null=False, blank=False, db_index=True, verbose_name=u'Плательщик')
	shipper		= models.ForeignKey(Org, null=False, blank=False, db_index=True, verbose_name=u'Поставщик')
	#supplier	= models.CharField(max_length=64, null=True, blank=True, db_index=False, verbose_name=u'Продавец')	# max=38
	billno		= models.CharField(max_length=32, db_index=True, verbose_name=u'Номер счета')	# max=11
	billdate	= models.DateField(db_index=True, verbose_name=u'Дата счета')
	billsum		= models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Сумма счета')
	payedsum	= models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Оплачено')
	topaysum	= models.DecimalField(max_digits=11, decimal_places=2, db_index=True, verbose_name=u'Сумма к оплате')
	assign		= models.ForeignKey(Approver, related_name='assigned', db_index=True, verbose_name=u'Исполнитель')
	rpoint		= models.ForeignKey('Route', null=True, blank=True, related_name='rbill', db_index=True, verbose_name=u'Точка маршрута')
	#done		= models.NullBooleanField(null=True, blank=True, verbose_name=u'Закрыт')
	state		= models.ForeignKey(State, db_index=True, verbose_name=u'Состояние')
	locked		= models.BooleanField(null=False, blank=False, default=False, db_index=True, verbose_name=u'В работе')
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
		if (self.state.pk == 5) and (self.locked):
			return 'Aquamarine'
		else:
			return self.state.color
	def	get_mgr(self):
		return self.route_set.get(order=ORD_MGR)
		#return self.route_set.get(role=ROLE_CHIEF)

	def	get_boss(self):
		return self.route_set.get(order=ORD_BOSS)
		#return self.route_set.get(role=ROLE_BOSS)

	class   Meta:
		unique_together		= (('shipper', 'billno', 'billdate'),)
		#ordering		= ('-fileseq_id',)
		verbose_name		= u'Счет'
		verbose_name_plural	= u'Счета'

class	Route(models.Model):
	bill	= models.ForeignKey(Bill, db_index=True, verbose_name=u'Счет')
	# 1-based route point (assignee excluded)
	order	= models.PositiveSmallIntegerField(null=False, blank=False, db_index=True, verbose_name=u'#')
	role	= models.ForeignKey(Role, db_index=True, verbose_name=u'Роль')
	approve	= models.ForeignKey(Approver, null=True, blank=True, db_index=True, verbose_name=u'Подписант')
	#state	= models.ForeignKey(State, verbose_name=u'Состояние')
	#action	= models.CharField(max_length=16, verbose_name=u'Действие')

	def	__unicode__(self):
		return '%d.%d: %s' % (self.bill.pk, self.order, self.approve.get_fio() if self.approve else self.role.name)

	def	get_str(self):
		#return self.approve.get_fio() if self.approve else self.role.name
		return self.approve.user.last_name if self.approve else self.role.name

	class   Meta:
		unique_together		= (('bill', 'order',), ('bill', 'role'))
		ordering                = ('bill', 'order',)
		verbose_name            = u'Точка маршрута'
		verbose_name_plural     = u'Точки маршрута'

class	Event(models.Model):
	bill	= models.ForeignKey(Bill, related_name='events', db_index=True, verbose_name=u'Счет')
	approve	= models.ForeignKey(Approver, db_index=True, verbose_name=u'Подписант')
	resume	= models.BooleanField(db_index=True, verbose_name=u'Резолюция')
	ctime	= models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=u'ДатаВремя')
	comment	= models.CharField(max_length=255, null=True, blank=True, db_index=True, verbose_name=u'Камменты')	# max=107

	def	__unicode__(self):
		return '%s: %s' % (self.approve, self.comment)

	class   Meta:
		ordering                = ('ctime',)
		verbose_name            = u'Резолюция'
		verbose_name_plural     = u'Резолюции'
