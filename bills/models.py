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

#state_id = {	# rpoint==None, done
#	(True,	None):	1,		# Draft
#	(False,	None ):	2,		# OnWay
#	(True,	True ):	3,		# Accepted
#	(True,	False):	4,		# Rejected
#}

state_id = {	# rpoint==None, done
	(True,	None):	1,		# Draft
	(False,	None ):	2,		# OnWay
	(False,	True):	3,		# OnPay
	(True,	True):	4,		# Accepted
	(True,	False):	5,		# Rejected
	(False,	False):	6,		# <impossible>
}

state_name = {	# rpoint==None, done
	(True,	None):	'Черновик',	# Draft
	(False,	None ):	'В пути',	# OnWay
	(False,	True):	'В оплате',	# OnPay
	(True,	True ):	'Исполнен',	# Accepted
	(True,	False):	'Завернут',	# Rejected
}

state_color = {	# rpoint==None, done	http://www.w3schools.com/html/html_colornames.asp
	(True,	None):	'white',	# Draft
	(False,	None ):	'FFFF99',	# OnWay (yellow)
	(False,	True):	'aqua',		# OnPay
	(True,	True ):	'chartreuse',	# Accepted (green)
	(True,	False):	'silver',	# Rejected (gray)
}

class	State(models.Model):
	'''
	Predefined Bill states:
	* onWay
	* согласовано
	[* оплачено]
	'''
	id	= models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'#')
	name	= models.CharField(max_length=16, verbose_name=u'Наименование')

	def	__unicode__(self):
		return self.name

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

class	Bill(models.Model):
	'''
	Fields:
	?desc:txt
	?ctime:datetime - время создания
	?etime:datetime - время окончания

	??Поставщик
	??Номер счета
	??Дата счета
	??Сумма счета
	TODO:
	* route = ManyToMany(User)
	* history = ManyToMany(User)
	* Object = FK
	* Depart = FK
	#created	= models.DateTimeField(auto_now_add=True, verbose_name=u'Создан')	# editable-False
	#updated	= models.DateTimeField(auto_now=True, verbose_name=u'Изменен')		# editable-False
	TODO: get_route_ok(user):
	* user not in route
	* route ends w/ accounter
	* route len > 0
	'''
	fileseq		= models.ForeignKey(FileSeq, related_name='bills', verbose_name=u'Файлы')
	project		= models.CharField(max_length=64, verbose_name=u'Объект')
	depart		= models.CharField(max_length=64, null=True, blank=True, verbose_name=u'Направление')
	supplier	= models.CharField(max_length=64, verbose_name=u'Поставщик')
	assign		= models.ForeignKey(Approver, related_name='assigned', verbose_name=u'Исполнитель')
	rpoint		= models.ForeignKey('Route', null=True, blank=True, related_name='rbill', verbose_name=u'Точка маршрута')
	done		= models.NullBooleanField(null=True, blank=True, verbose_name=u'Закрыт')
	#route		= SortedManyToManyField(Approver, null=True, blank=True, related_name='route', verbose_name=u'Маршрут')
	#history		= models.ManyToManyField(Approver, null=True, blank=True, related_name='history', through='BillEvent', verbose_name=u'История')

	def     __unicode__(self):
		return str(self.pk)

	def	__get_state(self):
		return (self.rpoint==None, self.done)

	def	get_state_id(self):
		return state_id[self.__get_state()]

	def	get_state_name(self):
		return state_name[self.__get_state()]

	def	get_state_color(self):
		return state_color[self.__get_state()]

	class   Meta:
		#unique_together		= (('scan', 'type', 'name'),)
		#ordering                = ('id',)
		verbose_name            = u'Счет'
		verbose_name_plural     = u'Счета'

class	Route(models.Model):
	bill	= models.ForeignKey(Bill, verbose_name=u'Счет')
	order	= models.PositiveSmallIntegerField(null=False, blank=False, verbose_name=u'#')
	role	= models.ForeignKey(Role, verbose_name=u'Роль')
	approve	= models.ForeignKey(Approver, null=True, blank=True, verbose_name=u'Подписант')
	state	= models.ForeignKey(State, verbose_name=u'Состояние')
	action	= models.CharField(max_length=16, verbose_name=u'Действие')

	def	__unicode__(self):
		return '%d.%d: %s' % (self.bill.pk, self.order, self.approve.get_fio() if self.approve else self.role.name)

	def	get_str(self):
		return self.approve.get_fio() if self.approve else self.role.name

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
	comment	= models.TextField(null=True, blank=True, verbose_name=u'Камменты')

	def	__unicode__(self):
		return '%s: %s' % (self.approve, self.comment)

	class   Meta:
		ordering                = ('ctime',)
		verbose_name            = u'Резолюция'
		verbose_name_plural     = u'Резолюции'

'''
class	RouteTemplate(models.Model):
	role	= models.ForeignKey(Role, verbose_name=u'Роль')
	approve	= models.ForeignKey(Approver, null=True, blank=True, verbose_name=u'Подписант')
	state	= models.ForeignKey(State, verbose_name=u'Состояние')
	areq	= models.BooleanField(verbose_name=u'Требует Подписанта')

	class   Meta:
		#unique_together		= (('scan', 'type', 'name'),)
		#ordering                = ('id',)
		verbose_name            = u'Шаблон маршрута'
		verbose_name_plural     = u'Шаблоны маршрутов'
'''
